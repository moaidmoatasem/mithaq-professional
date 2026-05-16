"""Unit tests for Business Process Mapper."""

from __future__ import annotations

import pytest
from cherenkov.compliance.process_mapper import PROCESSES, ProcessMapper


class TestProcessMapperListProcesses:
    def test_list_all_processes(self):
        processes = ProcessMapper.list_processes()
        assert len(processes) >= 7
        for proc in processes:
            assert "process_id" in proc
            assert "name" in proc
            assert "category" in proc
            assert "step_count" in proc

    def test_list_processes_by_category(self):
        processes = ProcessMapper.list_processes(category="authentication")
        assert len(processes) >= 2
        for proc in processes:
            assert proc["category"] == "authentication"

    def test_list_processes_empty_category(self):
        processes = ProcessMapper.list_processes(category="nonexistent")
        assert len(processes) == 0


class TestProcessMapperGetProcess:
    def test_get_valid_process(self):
        process = ProcessMapper.get_process("user_authentication")
        assert process is not None
        assert process["process_id"] == "user_authentication"
        assert len(process["steps"]) == 4
        for step in process["steps"]:
            assert "step_id" in step
            assert "name" in step
            assert "controls" in step
            for control in step["controls"]:
                assert "cwe_id" in control
                assert "compliance" in control

    def test_get_invalid_process(self):
        process = ProcessMapper.get_process("nonexistent_process")
        assert process is None

    def test_process_steps_have_controls(self):
        process = ProcessMapper.get_process("payment_processing")
        assert process is not None
        for step in process["steps"]:
            assert len(step["controls"]) > 0
            for control in step["controls"]:
                assert control["cwe_id"].startswith("CWE-")


class TestProcessMapperGetProcessControls:
    def test_get_controls_all_frameworks(self):
        result = ProcessMapper.get_process_controls("user_authentication")
        assert "error" not in result
        assert result["process_id"] == "user_authentication"
        assert result["total_unique_cwes"] > 0
        assert result["framework_filter"] == "all"
        assert len(result["step_controls"]) == 4

    def test_get_controls_filtered_framework(self):
        result = ProcessMapper.get_process_controls("user_authentication", framework="OWASP")
        assert "error" not in result
        assert result["framework_filter"] == "OWASP"
        for step in result["step_controls"]:
            for control in step["controls"]:
                assert "framework_controls" in control

    def test_get_controls_invalid_process(self):
        result = ProcessMapper.get_process_controls("nonexistent")
        assert "error" in result
        assert result["controls"] == []


class TestProcessMapperGenerateRiskReport:
    def test_generate_valid_report(self):
        report = ProcessMapper.generate_risk_report("payment_processing")
        assert "error" not in report
        assert report["process_id"] == "payment_processing"
        assert "risk_summary" in report
        assert "compliance_coverage" in report
        assert report["risk_summary"]["total_steps"] == 5
        assert report["risk_summary"]["average_risk_score"] > 0
        assert report["risk_summary"]["max_risk_score"] >= 3
        assert len(report["unique_cwes"]) > 0

    def test_generate_invalid_report(self):
        report = ProcessMapper.generate_risk_report("nonexistent")
        assert "error" in report

    def test_report_compliance_coverage(self):
        report = ProcessMapper.generate_risk_report("user_authentication")
        coverage = report["compliance_coverage"]
        for fw in ["OWASP", "SAMA_CSF", "EGY_FIN_CSF", "DORA"]:
            assert fw in coverage
            assert "controls_mapped" in coverage[fw]
            assert "coverage_percentage" in coverage[fw]

    def test_report_risk_levels(self):
        report = ProcessMapper.generate_risk_report("admin_operations")
        assert len(report["risk_summary"]["critical_steps"]) >= 2
        assert report["risk_summary"]["max_risk_score"] == 4


class TestProcessMapperCategories:
    def test_list_categories(self):
        categories = ProcessMapper.list_categories()
        assert isinstance(categories, list)
        assert len(categories) >= 4
        assert "authentication" in categories
        assert "financial" in categories
        assert categories == sorted(categories)


class TestProcessDataIntegrity:
    def test_all_processes_have_steps(self):
        for proc_id, proc in PROCESSES.items():
            assert len(proc.steps) > 0, f"{proc_id} has no steps"

    def test_all_steps_have_cwes(self):
        for proc_id, proc in PROCESSES.items():
            for step in proc.steps:
                assert len(step.cwe_ids) > 0, f"{proc_id}/{step.step_id} has no CWEs"

    def test_all_cwes_are_valid_format(self):
        for proc in PROCESSES.values():
            for step in proc.steps:
                for cwe_id in step.cwe_ids:
                    assert cwe_id.startswith("CWE-"), f"Invalid CWE format: {cwe_id}"

    def test_all_risk_levels_valid(self):
        valid_levels = {"low", "medium", "high", "critical"}
        for proc in PROCESSES.values():
            for step in proc.steps:
                assert step.risk_level in valid_levels, f"Invalid risk level: {step.risk_level}"
