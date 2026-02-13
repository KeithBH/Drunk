import { edgeBaseUrl, supabase } from "./supabase";
import { RecognitionResult } from "../types";

export async function recognizeBeverage(payload: {
  photoUrl?: string;
  barcode?: string;
  locale?: string;
}): Promise<RecognitionResult> {
  if (!edgeBaseUrl) {
    throw new Error("Missing edge function base URL.");
  }

  const { data: sessionData } = await supabase.auth.getSession();
  const token = sessionData.session?.access_token || "";

  const response = await fetch(`${edgeBaseUrl}/recognize-beverage`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : ""
    },
    body: JSON.stringify({
      photoUrl: payload.photoUrl || null,
      barcode: payload.barcode || null,
      locale: payload.locale || "zh-CN",
      userId: sessionData.session?.user?.id || null
    })
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Recognition failed.");
  }

  return (await response.json()) as RecognitionResult;
}
