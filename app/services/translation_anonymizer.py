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

    def analyze_and_anonymize(self, text: str, language: str) -> Tuple[str, List[Dict[str, Any]]]:
        if not text or not language:
            return text, []

        analyzer_results = self.analyzer.analyze(text=text, language=language)
        if not analyzer_results:
            return text, []

        unique_spans: Dict[Tuple[int, int], Any] = {}
        for res in sorted(analyzer_results, key=lambda r: (r.start, -r.score)):
            key = (res.start, res.end)
            if key not in unique_spans:
                unique_spans[key] = res

        masked_results = list(unique_spans.values())
        masked_results.sort(key=lambda r: r.start)

        operators = {
            res.entity_type: OperatorConfig("replace", {"new_value": f"<{res.entity_type}>"})
            for res in masked_results
        }

        anon_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=masked_results,
            operators=operators,
        )
        anonymized_text_generic = anon_result.text

        mapping_list: List[Dict[str, Any]] = []
        anonymized_text = anonymized_text_generic
        for idx, res in enumerate(masked_results):
            placeholder = f"<{res.entity_type}_{idx}>"
            mapping_list.append({
                "placeholder": placeholder,
                "start": res.start,
                "end": res.end,
                "entity_type": res.entity_type,
                "original": text[res.start:res.end],
            })

            generic = f"<{res.entity_type}>"
            anonymized_text = anonymized_text.replace(generic, placeholder, 1)

        return anonymized_text, mapping_list

