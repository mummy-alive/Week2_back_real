import json
import google.generativeai as genai

#GEMINI_API_URL = 'https://api.gemini.com/v1/analyze'  # Replace with the actual Gemini API URL

def AIMatchmake(user_profile, other_profiles):
    genai.configure(api_key='AIzaSyB7y9Bji5w_rlYPkn6bdwbt83kKMjK7yvw')

    model = genai.models.get('gemini-1.5-flash')
    prompt = f"""
    List the most suitable teammates from the given user profile. Use the following JSON schema for the response: 
    The list shall be sorted in descending order based on compatibility.
    Each email should be represented as a dictionary: `Email = {{"email": str }}`
    Return a `list[Email]`
    
    Here is the user's profile for reference: {json.dumps(user_profile)}
    Here is the list of other profiles: {json.dumps(other_profiles)}
    """
    repeat = 0
    while repeat < 5:
        try:
            response = model.generate(prompt=prompt, max_tokens=200)
            response_data = json.loads(response.generations[0].text)
            return response_data
        except Exception as e:
            print(f"Error in AIMatchmake: {e}")
            repeat += 1    
    return []