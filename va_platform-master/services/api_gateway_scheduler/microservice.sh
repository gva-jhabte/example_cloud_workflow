gcloud run services list --region europe-west1 --platform managed | awk 'NR>1{print $2}' > output.yaml
