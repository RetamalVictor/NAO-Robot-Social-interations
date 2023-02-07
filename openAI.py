import openai


class openAI:
    def response(self, prompt: str):
        self.prompt = prompt + "?\n"

        openai.api_key = "<Your key>"

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=self.prompt,
            temperature=0.7,
            max_tokens=75,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n\n"],
        )
        return (response["choices"][0])["text"]

