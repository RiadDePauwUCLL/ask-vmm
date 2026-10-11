from __future__ import annotations

import os
import re
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

import requests
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

LOGGER = logging.getLogger(__name__)
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
REFUSAL_SCORE_THRESHOLD = 0.02

REPORTS: List[Tuple[str, str]] = [
    (
        "gemeenschappelijke_maas_waterkwaliteit.pdf",
        "https://vmm.vlaanderen.be/pers/persbericht_gezamenlijke_monitoring_waterkwaliteit_gemeenschappelijke_maas_tw.pdf/@@download/file",
    ),
    (
        "luchtkwaliteitsmeetcampagne_2021.pdf",
        "https://vmm.vlaanderen.be/pers/20210927_persbericht_luchtkwaliteitsmeetcampagne_tw.pdf/@@download/file",
    ),
    (
        "educatief_pakket_luchtkwaliteit.pdf",
        "https://vmm.vlaanderen.be/tips/lucht/luchteducatie/educatief-pakket-luchtkwaliteit.pdf/@@download/file",
    ),
    (
        "beltair_persbericht.pdf",
        "https://vmm.vlaanderen.be/pers/belaqi_pers_nl_tw.pdf/@@download/file",
    ),
    (
        "luchtbeleidsplan_bijlage_4.pdf",
        "https://vmm.vlaanderen.be/publicaties/luchtbeleidsplan-2030/5-vr-2019-2510-doc-1118-6-bijlage-4-lkzones.pdf/@@download/file",
    ),
]

STOPWORDS = {
    "de", "het", "een", "van", "in", "op", "voor", "met", "door", "naar", "bij", "is", "wordt",
    "dat", "als", "aan", "uit", "over", "om", "te", "na", "welke", "wat", "hoe", "waarom",
    "zijn", "heeft", "verder", "zoals", "dan", "geen", "mijn", "jouw", "ons", "hun", "daar", "hier"
}


@dataclass
class Chunk:
    doc_name: str
    page_number: int
    text: str
    source_url: str = ""


class VMMQA:
    def __init__(self, reports_dir: str | Path | None = None):
        self.reports_dir = Path(reports_dir) if reports_dir else Path("data/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.chunks: List[Chunk] = []
        self.vectorizer = None
        self.matrix = None
        self.char_vectorizer = None
        self.char_matrix = None
        self._load_reports()

    def _download_report(self, filename: str, url: str) -> Path:
        destination = self.reports_dir / filename
        if destination.exists():
            return destination

        response = requests.get(
            url,
            timeout=60,
            allow_redirects=True,
            headers={"User-Agent": "Ask-VMM/1.0"},
        )
        response.raise_for_status()
        destination.write_bytes(response.content)
        return destination

    def _load_reports(self) -> None:
        self.chunks = []
        for filename, url in REPORTS:
            try:
                file_path = self._download_report(filename, url)
                self._extract_pdf(file_path, url)
            except requests.RequestException:
                LOGGER.exception("Could not download VMM report: %s", filename)

        if not self.chunks:
            return

        texts = [chunk.text for chunk in self.chunks]
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            strip_accents="unicode",
            stop_words=list(STOPWORDS),
            min_df=1,
        )
        self.matrix = self.vectorizer.fit_transform(texts)
        self.char_vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=1,
        )
        self.char_matrix = self.char_vectorizer.fit_transform(texts)

    def _extract_pdf(self, file_path: Path, source_url: str) -> None:
        try:
            reader = PdfReader(str(file_path))
        except Exception:
            LOGGER.exception("Could not read PDF: %s", file_path)
            return

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            for chunk_text in self._chunk_page(text):
                self.chunks.append(
                    Chunk(
                        doc_name=file_path.name,
                        page_number=page_num,
                        text=chunk_text,
                        source_url=source_url,
                    )
                )

    def _normalize_text(self, text: str) -> str:
        text = text.replace("\x00", " ")
        text = text.replace("\u00a0", " ")
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line)

    def _chunk_page(self, text: str) -> List[str]:
        cleaned = self._normalize_text(text)
        if not cleaned:
            return []

        chunks = []
        start = 0
        while start < len(cleaned):
            end = min(start + CHUNK_SIZE, len(cleaned))
            chunks.append(cleaned[start:end].strip())
            if end == len(cleaned):
                break
            start = end - CHUNK_OVERLAP
        return chunks
    def _clean_question(self, question: str) -> str:
        return re.sub(r"\s+", " ", question).strip()

    def _sentence_score(self, sentence: str, question: str) -> float:
        q_tokens = {token.lower() for token in re.findall(r"[a-zA-Z0-9]+", question) if token.lower() not in STOPWORDS}
        s_tokens = {token.lower() for token in re.findall(r"[a-zA-Z0-9]+", sentence) if token.lower() not in STOPWORDS}
        if not q_tokens:
            return 0.0
        overlap = len(q_tokens & s_tokens)
        if overlap == 0:
            return 0.0
        return overlap + 0.5 * (1 if any(char.isdigit() for char in sentence) else 0)

    def _answer_from_chunk(self, question: str, chunk: Chunk) -> str:
        sentences = re.split(r"(?<=[.!?])\s+|\n+", chunk.text)
        if not sentences:
            return chunk.text[:400]

        ranked = sorted(sentences, key=lambda s: self._sentence_score(s, question), reverse=True)
        best = ranked[0]
        if len(best) > 450:
            best = best[:450].rsplit(" ", 1)[0] + "..."
        return best.strip()

    def answer_question(
        self,
        question: str,
        refusal_score_threshold: float = REFUSAL_SCORE_THRESHOLD,
    ) -> Tuple[str, List[Tuple[str, int]]]:
        if (
            not self.chunks
            or self.matrix is None
            or self.vectorizer is None
            or self.char_matrix is None
            or self.char_vectorizer is None
        ):
            return "Ik weet het niet. Ik kon geen documenten laden.", []

        cleaned_question = self._clean_question(question)
        if not cleaned_question:
            return "Ik weet het niet. Ik heb geen vraag ontvangen.", []

        word_query_vector = self.vectorizer.transform([cleaned_question])
        char_query_vector = self.char_vectorizer.transform([cleaned_question])
        word_scores = cosine_similarity(word_query_vector, self.matrix).ravel()
        char_scores = cosine_similarity(char_query_vector, self.char_matrix).ravel()
        scores = 0.75 * word_scores + 0.25 * char_scores
        top_indices = scores.argsort()[-3:][::-1]
        selected = [(scores[idx], self.chunks[idx]) for idx in top_indices if scores[idx] > 0.0]

        if not selected:
            return "Ik weet het niet. Ik kon in deze documenten geen antwoord vinden.", []

        best_score, best_chunk = max(selected, key=lambda item: item[0])
        if best_score < refusal_score_threshold:
            return "Ik weet het niet. Ik kon in deze documenten geen antwoord vinden.", []

        answer = self._answer_from_chunk(cleaned_question, best_chunk)

        question_tokens = {
            token.lower()
            for token in re.findall(r"[a-zA-Z0-9]+", cleaned_question)
            if token.lower() not in STOPWORDS and len(token) > 2
        }
        answer_tokens = {
            token.lower()
            for token in re.findall(r"[a-zA-Z0-9]+", answer)
            if token.lower() not in STOPWORDS and len(token) > 2
        }
        chunk_tokens = {
            token.lower()
            for token in re.findall(r"[a-zA-Z0-9]+", best_chunk.text)
            if token.lower() not in STOPWORDS and len(token) > 2
        }

        answer_overlap = len(question_tokens & answer_tokens)
        chunk_overlap = len(question_tokens & chunk_tokens)
        strong_cross_language_match = best_score >= 0.18 and answer_overlap >= 1
        if question_tokens and chunk_overlap < 2 and answer_overlap < 2 and not strong_cross_language_match:
            return "Ik weet het niet. Ik kon in deze documenten geen antwoord vinden.", []

        sources = [(chunk.doc_name, chunk.page_number) for (_, chunk) in selected[:3]]
        return answer, sources

    def list_documents(self) -> List[str]:
        unique = []
        seen = set()
        for chunk in self.chunks:
            name = chunk.doc_name
            if name not in seen:
                seen.add(name)
                unique.append(name)
        return unique
