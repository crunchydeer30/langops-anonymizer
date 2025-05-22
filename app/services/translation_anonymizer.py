import logging
from typing import Tuple, List, Dict, Any

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

logger = logging.getLogger(__name__)

class TranslationAnonymizerService:
    def __init__(self, settings: Any = None):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.entity_mappings: Dict[str, Dict[str, Any]] = {}

    def analyze_and_anonymize(
        self, text: str, language: str, session_id: str = "default"
    ) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]], List[Dict[str, str]]]:
        if not text or not language:
            return text, {}, [], []

        analyzer_results = self.analyzer.analyze(text=text, language=language)
        if not analyzer_results:
            return text, {}, [], []

        mapping: Dict[str, Dict[str, Any]] = {}
        counts: Dict[str, int] = {}
        analysis_results_output: List[Dict[str, Any]] = []
        analyzer_results = sorted(analyzer_results, key=lambda r: r.start)
        for result in analyzer_results:
            etype = result.entity_type
            start, end = result.start, result.end
            orig = text[start:end]
            idx = counts.get(etype, 0)
            counts[etype] = idx + 1
            key = f"{start}:{end}"
            mapping[key] = {"value": orig, "entity_type": etype, "index": idx}
            analysis_results_output.append({
                "entity_type": etype,
                "start": start,
                "end": end,
                "score": result.score,
                "value": orig,
            })

        operators: Dict[str, OperatorConfig] = {}
        for etype in counts:
            operators[etype] = OperatorConfig(
                "replace", {"new_value": f"<{etype}>"}
            )

        anon_result = self.anonymizer.anonymize(
            text=text, analyzer_results=analyzer_results, operators=operators
        )
        anonymized_text = anon_result.text

        replacement_list: List[Dict[str, str]] = []
        for key, m in sorted(mapping.items(), key=lambda kv: int(kv[0].split(":")[0])):
            placeholder = f"<{m['entity_type']}>"
            replacement_list.append({"original": m["value"], "anonymized": placeholder})

        self.entity_mappings[session_id] = mapping
        return anonymized_text, mapping, analysis_results_output, replacement_list

    def deanonymize_translated(self, translated_text: str, session_id: str) -> str:
        """Replace <ENTITY_TYPE> tokens in translated text with original values in order."""
        if session_id not in self.entity_mappings:
            raise ValueError(f"No mappings found for session {session_id}")
        result = translated_text

        entries = sorted(
            self.entity_mappings[session_id].items(),
            key=lambda kv: int(kv[0].split(":")[0])
        )
        for _, m in entries:
            placeholder = f"<{m['entity_type']}>"
            result = result.replace(placeholder, m["value"], 1)
        return result

    def get_stored_mappings(self, session_id: str) -> Dict[str, Any]:
        """Return stored mappings for a session."""
        return self.entity_mappings.get(session_id, {})

    def clear_session(self, session_id: str) -> None:
        """Clear stored mappings for a session."""
        self.entity_mappings.pop(session_id, None)