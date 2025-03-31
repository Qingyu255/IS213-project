import { NextRequest, NextResponse } from "next/server";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { v4 as uuidv4 } from "uuid";

export const config = {
  runtime: "nodejs", // Use Node.js runtime for AWS SDK support
};

const s3Client = new S3Client({
  region: process.env.AWS_REGION || "ap-southeast-1",
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID || "",
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || "",
  },
});

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get("file") as File;

    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 });
    }

    const fileExtension = file.name.split(".").pop();
    const fileName = `events/${uuidv4()}.${fileExtension}`;
    const buffer = Buffer.from(await file.arrayBuffer());
    const bucketName =
      process.env.S3_BUCKET_NAME || "is213-project-dev-public-bucket";

    console.log(`Attempting to upload to bucket: ${bucketName}`);

    try {
      const command = new PutObjectCommand({
        Bucket: bucketName,
        Key: fileName,
        Body: buffer,
        ContentType: file.type,
        ACL: "public-read", // Make file publicly accessible
      });

      await s3Client.send(command);
      console.log(`Successfully uploaded to S3: ${fileName}`);
    } catch (s3Error) {
      console.error("S3 Upload error:", s3Error);
    }
    const s3Url = `https://${bucketName}.s3.amazonaws.com/${fileName}`;
    return NextResponse.json({ url: s3Url });
  } catch (error) {
    console.error("Upload error:", error);
    return NextResponse.json(
      {
        error:
          error instanceof Error ? error.message : "Failed to upload image",
      },
      { status: 500 }
    );
  }
}
