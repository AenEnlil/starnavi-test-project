import json
import vertexai

from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from vertexai.generative_models import GenerativeModel

from app.config import get_settings


def get_credentials():
    project_path = str(Path().resolve())
    path = project_path + get_settings().GOOGLE_CLOUD_PROJECT_CREDENTIALS_PATH
    credentials = Credentials.from_service_account_file(path,
                                                        scopes=['https://www.googleapis.com/auth/cloud-platform'])
    if credentials.expired:
        credentials.refresh(Request())

    return credentials


vertexai.init(project=get_settings().GOOGLE_CLOUD_PROJECT_ID, location=get_settings().GOOGLE_CLOUD_PROJECT_LOCATION,
              credentials=get_credentials())

model = GenerativeModel(get_settings().AI_MODEL_NAME)


def get_validation_prompt(data: dict):
    validation_prompt = f"Analyze following data and check if its fields contains offensive language: {data}." \
                        f"Format your response in JsonFormat. It must contain 'result' field, which will contain " \
                        f"boolean value of this check and 'failed_fields' field which will contain name of " \
                        f"fields, that failed check"
    return validation_prompt


def get_generation_prompt(post: str, comment: str):
    generation_prompt = f'You an author of this post: {post}. Generate answer to following user comment: {comment}.' \
                        f'Your response should be related to this comment and your post. Response should be ' \
                        f'less than 1000 characters'
    return generation_prompt


def clear_response(response: str) -> str:
    opening_bracket = response.find('{')
    closing_bracket = response.find('}')
    return response[opening_bracket:closing_bracket+1]


def get_result_of_ai_validation(data: dict) -> dict:
    prompt = get_validation_prompt(data)
    response = model.generate_content(prompt)
    cleared_response = clear_response(response.text)
    validation_result = json.loads(cleared_response)
    return validation_result


def generate_answer_to_user_comment_as_author_of_post(post: str, comment: str) -> str:
    prompt = get_generation_prompt(post, comment)
    response = model.generate_content(prompt)
    return response.text
