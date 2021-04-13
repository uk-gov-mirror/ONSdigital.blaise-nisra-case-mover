service: nisra-case-mover
runtime: python37

env_variables:
  SFTP_PORT: _SFTP_PORT
  SFTP_HOST: _SFTP_HOST
  SFTP_USERNAME: _SFTP_USERNAME
  SFTP_PASSWORD: _SFTP_PASSWORD
  INSTRUMENT_SOURCE_PATH: ''
  SURVEY_SOURCE_PATH: _SURVEY_SOURCE_PATH
  INSTRUMENT_DESTINATION_PATH: _INSTRUMENT_DESTINATION_PATH
  NISRA_BUCKET_NAME: _NISRA_BUCKET_NAME
  BLAISE_API_URL: _BLAISE_API_URL
  SERVER_PARK: _SERVER_PARK

vpc_access_connector:
  name: projects/_PROJECT_ID/locations/europe-west2/connectors/vpcconnect

basic_scaling:
  idle_timeout: 1800s
  max_instances: 1

handlers:
- url: /.*
  script: auto
  secure: always
  redirect_http_response_code: 301
  login: admin
