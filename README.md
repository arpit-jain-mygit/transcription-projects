[# transcription-projects
](https://myaccount.google.com/apppasswords

❯ export EMAIL_FROM=sachin.arpit.learning@gmail.com
❯ export EMAIL_TO=sachin.arpit.learning@gmail.com
❯ export EMAIL_APP_PASSWORD="zbjzgiypikmqquia"


gcloud projects describe transcribe-serverless \
  --format="value(projectNumber)"

service-320763587900@gcp-sa-eventarc.iam.gserviceaccount.com


gsutil iam ch \
  serviceAccount:service-320763587900@gcp-sa-eventarc.iam.gserviceaccount.com:roles/storage.legacyBucketReader \
  gs://jain-audio-input

gcloud services enable eventarc.googleapis.com

gcloud projects list

gcloud config set project transcription-project-484212

gcloud auth application-default set-quota-project transcription-project-484212

gcloud projects add-iam-policy-binding transcription-project-484212 \
  --member="serviceAccount:803238586922-compute@developer.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder"


gcloud projects add-iam-policy-binding transcription-project-484212 \
  --member="serviceAccount:803238586922-compute@developer.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"


gcloud projects add-iam-policy-binding transcription-project-484212 \
  --member="serviceAccount:803238586922-compute@developer.gserviceaccount.com" \
  --role="roles/run.admin"


gcloud projects add-iam-policy-binding transcription-project-484212 \
  --member="serviceAccount:803238586922-compute@developer.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gsutil iam ch \
  serviceAccount:service-803238586922@gcp-sa-eventarc.iam.gserviceaccount.com:roles/storage.legacyBucketReader \
  gs://jain-audio-input

gcloud projects add-iam-policy-binding transcription-project-484212 \
  --member="serviceAccount:803238586922-compute@developer.gserviceaccount.com" \
  --role="roles/eventarc.eventReceiver"

gcloud run services describe gemini-transcriber \
  --region asia-south1 \
  --format="value(spec.template.spec.serviceAccountName)"

803238586922-compute@developer.gserviceaccount.com

gcloud projects add-iam-policy-binding transcription-project-484212 \
  --member="serviceAccount:service-803238586922@gs-project-accounts.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"

gcloud run services add-iam-policy-binding gemini-transcriber \
  --region asia-south1 \
  --member="allUsers" \
  --role="roles/run.invoker"


gcloud eventarc triggers create mp3-input-trigger \
  --location=asia-south1 \
  --destination-run-service=gemini-transcriber \
  --destination-run-region=asia-south1 \
  --service-account=803238586922-compute@developer.gserviceaccount.com \
  --event-filters="type=google.cloud.storage.object.v1.finalized" \
  --event-filters="bucket=jain-audio-input"

gsutil cp /Users/arpitjain/Downloads/V1-Part1-C1.mp3 gs://jain-audio-input/

Change -10M to:
-5M → last 5 minutes
-2M → last 2 minutes

gcloud logging read \
  'resource.type="cloud_run_revision"
   AND resource.labels.service_name="gemini-transcriber"
   AND timestamp >= "'$(date -u -v-10M +"%Y-%m-%dT%H:%M:%SZ")'"' \
  --order=asc \
  --format=json \
| jq -r '.[] |
  (
    (.timestamp
      | sub("\\.[0-9]+Z$"; "Z")
      | fromdateiso8601
      + 19800
      | strftime("%Y-%m-%d %H:%M:%S IST")
    )
    + " | " + (.textPayload // "")
  )'



gcloud secrets create youtube-cookies \
  --replication-policy=automatic


gcloud secrets versions add youtube-cookies \
  --data-file=/Users/arpitjain/Downloads/youtube_cookies.txt

gcloud secrets versions list youtube-cookies

gcloud secrets add-iam-policy-binding youtube-cookies \
  --member="serviceAccount:803238586922-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud run deploy gemini-transcriber \
  --source gemini-transcriber \
  --region asia-south1 \
  --set-env-vars "EMAIL_FROM=$EMAIL_FROM,EMAIL_TO=$EMAIL_TO,EMAIL_APP_PASSWORD=$EMAIL_APP_PASSWORD,GEMINI_API_KEY=$GEMINI_API_KEY" \
  --set-secrets "/secrets/youtube_cookies.txt=youtube-cookies:latest" \
  --no-allow-unauthenticated


curl -X POST \
  https://gemini-transcriber-803238586922.asia-south1.run.app/youtube \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=3ZYsuS8y2nM&list=PLZjCHQlC6ES7qlrevDrnPDedgb2tPwa1d&index=97"}'


=======

🛡️ Optional but Recommended Next Steps

Now that everything works, you may want to:

🔐 Move secrets to Secret Manager

⏱ Increase Cloud Run timeout for long audios

🔁 Add retry / failure bucket

📧 Add daily summary email

✂️ Chunk very long pravachans automatically




)
