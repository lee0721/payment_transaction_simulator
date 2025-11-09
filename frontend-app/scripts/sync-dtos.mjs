import { promises as fs } from "node:fs";
import path from "node:path";

const source = path.resolve(process.cwd(), "../shared/dtos/openapi.json");
const destinationDir = path.resolve(process.cwd(), "src/generated");
const destination = path.join(destinationDir, "openapi.json");

async function main() {
  try {
    await fs.access(source);
  } catch {
    console.error("shared/dtos/openapi.json not found. Run the backend export script first.");
    process.exit(1);
  }

  await fs.mkdir(destinationDir, { recursive: true });
  await fs.copyFile(source, destination);
  console.log(`Synced OpenAPI spec to ${destination}`);
}

main();
