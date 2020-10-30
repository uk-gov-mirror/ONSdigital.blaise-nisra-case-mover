apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: nisra-mover-opn
spec:
  schedule: "10,40 * * * *"
  successfulJobsHistoryLimit: 5
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: nisra-mover-opn
            image: "eu.gcr.io/ons-blaise-dev/blaise-nisra-case-mover:COMMIT_SHA"
            env:
              - name: INSTRUMENT_SOURCE_PATH
                value: ''
              - name: SURVEY_SOURCE_PATH
                value: 'ONS/OPN/'
              - name: INSTRUMENT_DESTINATION_PATH
                value: 'OPN/'
              - name: NISRA_BUCKET_NAME
                value: 'ons-blaise-dev-nisra'
              - name: SFTP_HOST
                valueFrom:
                  secretKeyRef:
                    name: nisra-sftp
                    key: SFTP_HOST
              - name: SFTP_USERNAME
                valueFrom:
                  secretKeyRef:
                    name: nisra-sftp
                    key: SFTP_USERNAME
              - name: SFTP_PASSWORD
                valueFrom:
                  secretKeyRef:
                    name: nisra-sftp
                    key: SFTP_PASSWORD
              - name: SFTP_PORT
                valueFrom:
                  secretKeyRef:
                    name: nisra-sftp
                    key: SFTP_PORT
          restartPolicy: OnFailure
