import { createAzure } from "@ai-sdk/azure";
import { streamText, convertToCoreMessages } from "ai";
import { z } from "zod";

const azure = createAzure({
  resourceName: process.env.AZURE_RES_NAME,
  apiKey: process.env.AZURE_API_KEY,
});

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages, setup } = JSON.parse(await req.json());

  const body = JSON.stringify({ ...setup });

  const result = await streamText({
    model: azure("gpt-4o"),
    messages: convertToCoreMessages(messages),
    tools: {
      riddle: {
        description: "Present only one riddle to the user.",
        execute: async () => {
          try {
            const url = process.env.NEXT_PUBLIC_BACKEND_URL;
            if (!url) return;
            const res = await fetch(url, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify(JSON.parse(body)),
            });
            const content = await res.json();
            return {
              content,
            };
          } catch (error) {
            console.log(error);
          }
        },
        parameters: z.object({
          information: z
            .string()
            .describe(
              "Information about the riddle. Do not provide the answer and do not ask the riddle again!"
            ),
          motivation: z
            .string()
            .describe("Motivational sentence. Do not ask a question!"),
          name: z
            .string()
            .describe(
              "Question name. Do not provide the answer! Provide a name that fits the information."
            ),
        }),
      },
    },
  });

  return result.toDataStreamResponse();
}
