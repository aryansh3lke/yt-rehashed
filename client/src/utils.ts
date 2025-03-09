export const generateValidFilename = (filename: string) => {
  // Define the invalid characters (for most operating systems)
  const invalidChars = /[<>:"/\\|?*]/g;

  // Replace invalid characters with an underscore
  const sanitized = filename.replace(invalidChars, "_");

  // Trim leading and trailing whitespace
  const trimmed = sanitized.trim();

  // Remove any additional invalid characters (like null char)
  const finalFilename = trimmed.replace(/\0/g, "");

  return finalFilename;
};
