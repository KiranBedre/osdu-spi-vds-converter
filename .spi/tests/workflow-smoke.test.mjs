import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { test } from "node:test";
import { tmpdir } from "node:os";

import {
  getWorkflow,
  main,
} from "../acceptance/workflow-smoke.mjs";


const config = {
  workflowUrl: "https://example.test/api/workflow/v1",
  partition: "opendes",
  token: "token",
  workflowName: "segy-to-vds-conversion",
};


test("getWorkflow sends required headers", async () => {
  let request;
  const payload = await getWorkflow(config, async (url, options) => {
    request = { url, options };
    return {
      ok: true,
      status: 200,
      json: async () => ({ workflowName: config.workflowName }),
    };
  });

  assert.equal(payload.workflowName, config.workflowName);
  assert.equal(request.url, `${config.workflowUrl}/workflow/${config.workflowName}`);
  assert.equal(request.options.headers.Authorization, "Bearer token");
  assert.equal(request.options.headers["data-partition-id"], "opendes");
});


test("main writes JUnit when the response body times out", async () => {
  const report = join(tmpdir(), `vds-workflow-${process.pid}.xml`);
  const args = [
    "--workflow-url", config.workflowUrl,
    "--partition", config.partition,
    "--token", config.token,
    "--workflow-name", config.workflowName,
    "--report", report,
  ];

  const result = await main(args, async () => ({
    ok: true,
    status: 200,
    json: async () => {
      throw new DOMException("The operation timed out", "TimeoutError");
    },
  }));

  assert.equal(result, 1);
  const evidence = await readFile(report, "utf8");
  assert.match(evidence, /failures="1"/);
  assert.match(evidence, /TimeoutError/);
});
