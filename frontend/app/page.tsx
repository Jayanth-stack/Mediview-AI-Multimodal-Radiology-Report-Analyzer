import UploadForm from "../components/UploadForm";
export default function Page() {
  return (
    <div className="space-y-6">
      <p className="text-sm text-gray-600">Upload an image and optional report text to test the pipeline.</p>
      <UploadForm />
    </div>
  );
}

