/**
 * Formats job names for user display
 * Converts "job-xxxxx" to "Export xxxxx"
 */
export function formatJobName(jobName: string): string {
  const match = jobName.match(/^job-(.+)$/);
  if (match) {
    return `Export ${match[1]}`;
  }
  return jobName;
}
