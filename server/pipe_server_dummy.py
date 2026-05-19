from fastapi import FastAPI

from extraction.pipeline.medical_pipeline import MedicalPipeline

app = FastAPI()

pipeline = MedicalPipeline()


@app.post("/pipetest")
def pipetest():

    user_input = (
        "Ich habe seit etwa vier Tagen starke Kopfschmerzen, die vor allem morgens schlimmer sind und sich wie ein Druck hinter den Augen anfühlen. Dazu kommt, dass meine Nase ständig läuft und ich gelegentlich leichtes Fieber habe. Ich habe gestern angefangen, Ibuprofen zu nehmen, was die Schmerzen etwas lindert, aber nicht komplett wegnimmt. Außerdem bin ich vor einer Woche beim Joggen gestürzt und habe mir dabei das rechte Knie verletzt, es ist immer noch leicht geschwollen und schmerzt beim Treppensteigen. Ich bin mir nicht sicher, ob das alles zusammenhängt oder ob ich zwei verschiedene Probleme habe. Zusätzlich mache ich mir Sorgen, weil ich in letzter Zeit sehr müde bin und mich schlecht konzentrieren kann."
        #"Ich habe kopfschmerzen und gerade eine grippe glaube ich"
        #"Ich habe grippe und einen gebrochenen zeh"
        #"Mein hund hat durchfall und ich habe seit gestern starke kopfschmerzen"
        #"Wie geht es dir?"
        #"Ich brauche dringend einen arzttermin "
    )

    result = pipeline.run(user_input)

    return result.model_dump()