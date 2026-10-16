import { mkdir, writeFile } from "node:fs/promises";
import { dirname } from "node:path";
import { pathToFileURL } from "node:url";


function parseArguments(args) {
  const values = new Map();
  for (let index = 0; index < args.length; index += 2) {
    const name = args[index];
    const value = args[index + 1];
    if (!name?.startsWith("--") || value === undefined) {
      throw new Error(`Invalid argument at position ${index + 1}`);
    }
    values.set(name.slice(2), value);
  }

  const required = ["workflow-url", "partition", "token", "workflow-name", "report"];
  for (const name of required) {
    if (!values.has(name)) {
      throw new Error(`Missing required argument --${name}`);
    }
  }
  return Object.fromEntries(values);
}


function escapeXml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}


export async function getWorkflow(config, fetchImplementation = fetch) {
  const endpoint = `${config.workflowUrl.replace(/\/$/, "")}/workflow/` +
    encodeURIComponent(config.workflowName);
  const response = await fetchImplementation(endpoint, {
    headers: {
      Authorization: `Bearer ${config.token}`,
      "data-partition-id": config.partition,
    },
    signal: AbortSignal.timeout(30_000),
  });
  if (!response.ok) {
    throw new Error(`Workflow API returned HTTP ${response.status}`);
  }
  const payload = await response.json();
  if (payload === null || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("Workflow API response must be a JSON object");
  }
  return payload;
}


export async function writeJunit(report, failure = null) {
  const failureXml = failure === null
    ? ""
    : `<failure message="${escapeXml(failure)}">${escapeXml(failure)}</failure>`;
  const xml = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    `<testsuite name="vds-workflow-registration" tests="1" failures="${failure ? 1 : 0}">`,
    '<testcase classname="spi.vds" name="workflow_is_registered">',
    failureXml,
    "</testcase>",
    "</testsuite>",
    "",
  ].join("\n");
  await mkdir(dirname(report), { recursive: true });
  await writeFile(report, xml, "utf8");
}


export async function main(args = process.argv.slice(2), fetchImplementation = fetch) {
  let options;
  try {
    options = parseArguments(args);
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    return 2;
  }

  const config = {
    workflowUrl: options["workflow-url"],
    partition: options.partition,
    token: options.token,
    workflowName: options["workflow-name"],
  };
  try {
    await getWorkflow(config, fetchImplementation);
  } catch (error) {
    const message = `${error?.name ?? "Error"}: ${error?.message ?? String(error)}`;
    await writeJunit(options.report, message);
    console.error(message);
    return 1;
  }

  await writeJunit(options.report);
  console.log(`Workflow '${config.workflowName}' is registered`);
  return 0;
}


if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.exitCode = await main();
}
