import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class STTResultAnalyzer:
    def __init__(self, results_dir: str = "test_results"):
        self.results_dir = Path(results_dir)
        
    def load_all_results(self) -> List[Dict[str, Any]]:
        """Load all result files from the results directory."""
        results = []
        for result_file in self.results_dir.glob("*_results.json"):
            with open(result_file, 'r') as f:
                results.append(json.load(f))
        return results
    
    def calculate_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate various metrics from the test results."""
        metrics = {
            "total_files": len(results),
            "successful_transcriptions": {
                "deepgram": 0,
                "assemblyai": 0,
                "gladia": 0
            },
            "average_processing_time": {
                "deepgram": 0,
                "assemblyai": 0,
                "gladia": 0
            },
            "average_confidence": {
                "deepgram": 0,
                "assemblyai": 0,
                "gladia": 0
            }
        }
        
        deepgram_times = []
        assemblyai_times = []
        gladia_times = []
        deepgram_confidences = []
        assemblyai_confidences = []
        gladia_confidences = []
        
        for result in results:
            # Count successful transcriptions
            if result["services"]["deepgram"].get("success", False):
                metrics["successful_transcriptions"]["deepgram"] += 1
                deepgram_times.append(result["services"]["deepgram"]["processing_time"])
                deepgram_confidences.append(result["services"]["deepgram"]["confidence"])
            
            if result["services"]["assemblyai"].get("success", False):
                metrics["successful_transcriptions"]["assemblyai"] += 1
                assemblyai_times.append(result["services"]["assemblyai"]["processing_time"])
                assemblyai_confidences.append(result["services"]["assemblyai"]["confidence"])
            
            if result["services"]["gladia"].get("success", False):
                metrics["successful_transcriptions"]["gladia"] += 1
                gladia_times.append(result["services"]["gladia"]["processing_time"])
                gladia_confidences.append(result["services"]["gladia"]["confidence"])
        
        # Calculate averages
        if deepgram_times:
            metrics["average_processing_time"]["deepgram"] = sum(deepgram_times) / len(deepgram_times)
        if assemblyai_times:
            metrics["average_processing_time"]["assemblyai"] = sum(assemblyai_times) / len(assemblyai_times)
        if gladia_times:
            metrics["average_processing_time"]["gladia"] = sum(gladia_times) / len(gladia_times)
            
        if deepgram_confidences:
            metrics["average_confidence"]["deepgram"] = sum(deepgram_confidences) / len(deepgram_confidences)
        if assemblyai_confidences:
            metrics["average_confidence"]["assemblyai"] = sum(assemblyai_confidences) / len(assemblyai_confidences)
        if gladia_confidences:
            metrics["average_confidence"]["gladia"] = sum(gladia_confidences) / len(gladia_confidences)
        
        return metrics
    
    def generate_report(self, metrics: Dict[str, Any]):
        """Generate a detailed comparison report."""
        report = f"""
STT Services Comparison Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Files Tested: {metrics['total_files']}

Success Rate:
- Deepgram: {metrics['successful_transcriptions']['deepgram']}/{metrics['total_files']} ({metrics['successful_transcriptions']['deepgram']/metrics['total_files']*100:.1f}%)
- AssemblyAI: {metrics['successful_transcriptions']['assemblyai']}/{metrics['total_files']} ({metrics['successful_transcriptions']['assemblyai']/metrics['total_files']*100:.1f}%)
- Gladia: {metrics['successful_transcriptions']['gladia']}/{metrics['total_files']} ({metrics['successful_transcriptions']['gladia']/metrics['total_files']*100:.1f}%)

Average Processing Time:
- Deepgram: {metrics['average_processing_time']['deepgram']:.2f} seconds
- AssemblyAI: {metrics['average_processing_time']['assemblyai']:.2f} seconds
- Gladia: {metrics['average_processing_time']['gladia']:.2f} seconds

Average Confidence Score:
- Deepgram: {metrics['average_confidence']['deepgram']:.2f}
- AssemblyAI: {metrics['average_confidence']['assemblyai']:.2f}
- Gladia: {metrics['average_confidence']['gladia']:.2f}

Recommendation:
"""
        # Add recommendation based on metrics
        success_rates = {
            "Deepgram": metrics['successful_transcriptions']['deepgram'] / metrics['total_files'],
            "AssemblyAI": metrics['successful_transcriptions']['assemblyai'] / metrics['total_files'],
            "Gladia": metrics['successful_transcriptions']['gladia'] / metrics['total_files']
        }
        
        best_service = max(success_rates.items(), key=lambda x: x[1])[0]
        report += f"{best_service} shows the best reliability with highest success rate."
        
        processing_times = {
            "Deepgram": metrics['average_processing_time']['deepgram'],
            "AssemblyAI": metrics['average_processing_time']['assemblyai'],
            "Gladia": metrics['average_processing_time']['gladia']
        }
        
        fastest_service = min(processing_times.items(), key=lambda x: x[1])[0]
        report += f"\n{fastest_service} processes files the fastest."
        
        return report
    
    def save_report(self, report: str):
        """Save the report to a file."""
        report_file = self.results_dir / "comparison_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        logging.info(f"Report saved to {report_file}")

if __name__ == "__main__":
    analyzer = STTResultAnalyzer()
    results = analyzer.load_all_results()
    metrics = analyzer.calculate_metrics(results)
    report = analyzer.generate_report(metrics)
    analyzer.save_report(report)
    print(report) 