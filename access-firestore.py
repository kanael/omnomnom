cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

collection = db.collection(u'pokemons')

doc_ref = collection.document(u'Bulbasaur')
doc_ref.set({u'pokedex':1,u'type':u'grass'})
doc_ref = collection.document(u'Charmander')
doc_ref.set({u'pokedex':4,u'type':u'fire'})
doc_ref = collection.document(u'Pikachu')
doc_ref.set({u'pokedex':25,u'type':u'electric'})

for doc in collection.get():
    print (doc.id, " ", doc.to_dict())
