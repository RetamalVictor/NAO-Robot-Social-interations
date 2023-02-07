import openai


# class openAI:
#     def response(self, prompt: str):
#         self.prompt = prompt + "?\n"
#
#         openai.api_key = "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"
#
#         response = openai.Completion.create(
#             model="code-davinci-002",
#             prompt=self.prompt,
#             temperature=0.5,
#             max_tokens=60,
#             top_p=0.3,
#             frequency_penalty=0.5,
#             presence_penalty=0.2,
#             stop=["\n\n"],
#         )
#         return (response["choices"][0])["text"]

class openAI:
    def response(self, prompt: str):
        self.prompt = prompt + "?\n"

        openai.api_key = "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"

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



#
# import os
# import openai
#
# openai.api_key = os.getenv("OPENAI_API_KEY")
#
# response = openai.Completion.create(
#   model="text-davinci-003",
#   prompt="who is superman\n\nSuperman is a fictional superhero created by writer Jerry Siegel and artist Joe Shuster. He first appeared in Action Comics #1 in 1938 and has since become a highly recognized and beloved character in popular culture. Superman is an alien from the planet Krypton who was sent to Earth as an infant and raised as Clark Kent by a human family in Smallville, Kansas. He possesses extraordinary powers, including the ability to fly, superhuman strength, and invulnerability to most forms of physical harm. He fights crime using his powers and his keen intellect, and is one of the most recognizable and iconic superhero characters in the world.",
#   temperature=0.7,
#   max_tokens=256,
#   top_p=1,
#   frequency_penalty=0,
#   presence_penalty=0
# )