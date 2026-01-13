FROM python:3.10-slim
WORKDIR /app

# Install curl for downloading aws_signing_helper
RUN apt-get update && apt-get install -y curl

# Create .aws directory
RUN mkdir -p /root/.aws

# Download aws_signing_helper
RUN curl -L https://rolesanywhere.amazonaws.com/releases/1.1.1/X86_64/Linux/aws_signing_helper \
    -o /root/.aws/aws_signing_helper && \
    chmod +x /root/.aws/aws_signing_helper

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Create AWS config file with runtime environment variables\n\
cat > /root/.aws/config << EOF\n\
[profile default]\n\
credential_process = /root/.aws/aws_signing_helper credential-process \\\n\
  --certificate /root/.aws/certs/client.pem \\\n\
  --private-key /root/.aws/certs/client_private.key \\\n\
  --trust-anchor-arn ${TRUST_ANCHOR_ARN} \\\n\
  --profile-arn ${PROFILE_ARN} \\\n\
  --role-arn ${ROLE_ARN}\n\
EOF\n\
\n\
# Execute the original command\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

# Pip install
ADD src ./src
ADD pyproject.toml .
ADD setup.py .

RUN pip install . --no-cache-dir

ENTRYPOINT ["/entrypoint.sh"]
CMD ["fastapi", "run", "src/aind_metadata_service_server/main.py", "--port", "80"]
