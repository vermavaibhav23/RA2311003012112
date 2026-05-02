import http from "http";

const LOG_HOST = "20.207.122.201";
const LOG_PATH = "/evaluation-service/logs";
const ACCESS_TOKEN =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJ2djQ4MzRAc3JtaXN0LmVkdS5pbiIsImV4cCI6MTc3NzY5OTE0MCwiaWF0IjoxNzc3Njk4MjQwLCJpc3MiOiJBZmZvcmQgTWVkaWNhbCBUZWNobm9sb2dpZXMgUHJpdmF0ZSBMaW1pdGVkIiwianRpIjoiNDk1MDQ5NDgtNmM3MS00MmYwLTkzNDktZTE4Zjg3ODdiMzE5IiwibG9jYWxlIjoiZW4tSU4iLCJuYW1lIjoidmFpYmhhdiB2ZXJtYSIsInN1YiI6Ijg4MmYyYzhiLWZiNDAtNDQ1YS1hMjcwLTY1MzM0MDFlYTI2MiJ9LCJlbWFpbCI6InZ2NDgzNEBzcm1pc3QuZWR1LmluIiwibmFtZSI6InZhaWJoYXYgdmVybWEiLCJyb2xsTm8iOiJyYTIzMTEwMDMwMTIxMTIiLCJhY2Nlc3NDb2RlIjoiUWticHhIIiwiY2xpZW50SUQiOiI4ODJmMmM4Yi1mYjQwLTQ0NWEtYTI3MC02NTMzNDAxZWEyNjIiLCJjbGllbnRTZWNyZXQiOiJ1eE1lQndmQ1NKQ2dFZ1JWIn0.RyJaTP0HZ9G-7gcf-5CBCRy4mE6yp7mcDkCbiGJvUsM";

type Stack = "backend" | "frontend";
type Level = "debug" | "info" | "warn" | "error" | "fatal";
type Package =
  | "cache"
  | "controller"
  | "cron_job"
  | "db"
  | "domain"
  | "handler"
  | "repository"
  | "route"
  | "service"
  | "auth"
  | "config"
  | "middleware"
  | "utils";

export function Log(
  stack: Stack,
  level: Level,
  pkg: Package,
  message: string
): void {
  const body = JSON.stringify({ stack, level, package: pkg, message });

  const req = http.request(
    {
      hostname: LOG_HOST,
      path: LOG_PATH,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${ACCESS_TOKEN}`,
        "Content-Length": Buffer.byteLength(body),
      },
    },
    (res) => {
      res.resume();
    }
  );

  req.on("error", () => {});
  req.write(body);
  req.end();
}
