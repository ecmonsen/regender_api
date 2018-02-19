# This is for packaging code for the API Lambda function(s).
#
#
# Run this command from the root directory of the git repository:
#
# docker build -t project/lambda_builder -f docker/lambda_builder/Dockerfile .
#
#
# Build the lambda code with this command
#
# docker run -v $PWD:/external project/lambda_builder

#
FROM lambci/lambda:build-python2.7

# Set the working directory
WORKDIR /lambda_builder

ADD requirements.txt /lambda_builder/

# Install dependencies
RUN pip install virtualenv \
  && virtualenv /lambda_builder/venv --python $(which python2.7) \
  && . /lambda_builder/venv/bin/activate \
  && pip install -r /lambda_builder/requirements.txt


# Entry point is the builder.
ENTRYPOINT ["/bin/bash", "/external/docker/lambda_builder/zip_for_lambda.sh", "-v", "/lambda_builder/venv", "-s", "/external", "-o", "/external/built.zip", "-e", "/external/exclude.txt"]