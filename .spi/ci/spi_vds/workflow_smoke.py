from argparse import ArgumentParser
from dataclasses import dataclass
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class WorkflowCheck:
    workflow_url: str
    partition: str
    token: str
    workflow_name: str


def get_workflow(config: WorkflowCheck) -> dict[str, object]:
    endpoint = (
        f"{config.workflow_url.rstrip('/')}/workflow/"
        f"{quote(config.workflow_name, safe='')}"
    )
    request = Request(
        endpoint,
        headers={
            "Authorization": f"Bearer {config.token}",
            "data-partition-id": config.partition,
        },
    )
    with urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"Workflow API returned HTTP {response.status}")
        payload = json.loads(response.read())
    if not isinstance(payload, dict):
        raise ValueError("Workflow API response must be a JSON object")
    return payload


def write_junit(report: Path, failure: str | None) -> None:
    suite = ET.Element(
        "testsuite",
        name="vds-workflow-registration",
        tests="1",
        failures="1" if failure else "0",
    )
    case = ET.SubElement(
        suite,
        "testcase",
        classname="spi.vds",
        name="workflow_is_registered",
    )
    if failure:
        ET.SubElement(case, "failure", message=failure).text = failure
    report.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(suite).write(report, encoding="utf-8", xml_declaration=True)


def main() -> int:
    parser = ArgumentParser(description="Verify the VDS workflow registration")
    parser.add_argument("--workflow-url", required=True)
    parser.add_argument("--partition", required=True)
    parser.add_argument("--token", required=True)
    parser.add_argument("--workflow-name", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    config = WorkflowCheck(
        workflow_url=args.workflow_url,
        partition=args.partition,
        token=args.token,
        workflow_name=args.workflow_name,
    )

    try:
        get_workflow(config)
    except (HTTPError, URLError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        message = f"{type(error).__name__}: {error}"
        write_junit(args.report, message)
        print(message)
        return 1

    write_junit(args.report, None)
    print(f"Workflow '{config.workflow_name}' is registered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
