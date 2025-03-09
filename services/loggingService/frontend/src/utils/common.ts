export const getErrorStringFromResponse = async (res: Response): Promise<string> => {
  const resClone = res.clone();
  let errorData;
  try {
    errorData = await res.json();
  } catch (err) {
    // Use the cloned response to get the raw text
    const rawText = await resClone.text();
    errorData = {
      message: rawText || err || "Unexpected error, unable to parse response",
    };
  }
  return res.status + " " + res.statusText + errorData.error
    ? errorData.error
    : `${res.status}: ${
        errorData.stack || errorData.message || "An unexpected error occurred."
      }`;
};
