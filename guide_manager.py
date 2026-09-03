import random
from typing import Dict, List, Optional, Any
from database import Database
from monetization import monetization_engine


TRAVEL_GUIDES: List[Dict[str, Any]] = [
    {
        "id": "ryanair_bagaglio_gratuito",
        "title": "🎒 Come viaggiare con il SOLO bagaglio a mano gratuito (40x20x25) senza pagare supplementi",
        "destination": None,
        "amazon_query": "zaino viaggio cabina 40x20x25 ryanair",
        "content": (
            "💡 <b>GUIDA PRATICA SALVA-PORTAFOGLIO</b>\n\n"
            "Le compagnie low-cost come Ryanair, WizzAir ed EasyJet fanno pagare i bagagli da cabina più del volo stesso! Ecco come evitarlo legalmente:\n\n"
            "1️⃣ <b>Usa lo zaino giusto</b>: Non usare trolley rigidi. Uno zaino da 20-24 litri morbido entra sempre nel misuratore di metallo anche se è pieno.\n"
            "2️⃣ <b>Cubi di compressione</b>: Riducono il volume dei vestiti del 50% e tengono tutto in ordine.\n"
            "3️⃣ <b>Indossa i capi pesanti</b>: Giacca, felpa e scarpe più ingombranti indossali durante l'imbarco.\n"
            "4️⃣ <b>Tasca segreta</b>: Metti powerbank, cavi e documenti nelle tasche della giacca per liberare spazio nello zaino.\n\n"
            "👇 <i>Scopri lo zaino omologato più venduto e gli accessori consigliati con i link qui sotto:</i>"
        )
    },
    {
        "id": "scovare_errori_di_prezzo",
        "title": "🚨 I trucchi per prenotare un Errore di Prezzo (Error Fare) prima che scada",
        "destination": None,
        "amazon_query": "adattatore universale da viaggio rapido",
        "content": (
            "⚡ <b>GUIDA: COME FUNZIONANO GLI ERRORI DI PREZZO?</b>\n\n"
            "Un 'Error Fare' è uno sbaglio umano o un bug nei sistemi informatici delle compagnie aeree che azzera le tasse carburante o inserisce tariffe errate (es. volo A/R per New York a 150€).\n\n"
            "📌 <b>LE 3 REGOLE D'ORO:</b>\n"
            "1️⃣ <b>Prenota ALL'ISTANTE</b>: Un errore dura da 20 minuti a poche ore prima di essere corretto.\n"
            "2️⃣ <b>NON CHIAMARE LA COMPAGNIA</b>: Chiamare il servizio clienti fa scoprire subito l'errore e lo fa cancellare per tutti.\n"
            "3️⃣ <b>Aspetta a prenotare gli hotel non rimborsabili</b>: Attendi 7-14 giorni che il biglietto elettronico sia confermato definitivamente prima di bloccare alloggi e tour (o prenota sempre con <i>Cancellazione Gratuita</i>).\n\n"
            "👉 Attiva le notifiche di questo canale per non perdere i prossimi alert immediati!"
        )
    },
    {
        "id": "weekend_budapest_lowcost",
        "title": "🇭🇺 Weekend low-cost a Budapest con meno di 150€: Itinerario e consigli",
        "destination": "Budapest",
        "amazon_query": "power bank compatto viaggio ricarica rapida",
        "content": (
            "🏰 <b>MINI-GUIDA: WEEKEND A BUDAPEST LOW COST</b>\n\n"
            "Budapest è una delle capitali più spettacolari ed economiche d'Europa:\n\n"
            "🛁 <b>Terme Széchenyi o Gellért</b>: Esperienza imperdibile, rilassati nelle vasche termali all'aperto circondate da palazzi storici.\n"
            "🍺 <b>Ruin Bar nel quartiere ebraico</b>: Bevi una birra da <i>Szimpla Kert</i>, il pub ricavato in una vecchia fabbrica abbandonata.\n"
            "🌉 <b>Tram 2 lungo il Danubio</b>: Il percorso panoramico più bello del mondo al costo di un normale biglietto urbano da 1,20€!\n"
            "🍽️ <b>Dove mangiare</b>: Mercato Centrale (Nagy Vásárcsarnok) per assaggiare il vero Goulash a meno di 5€.\n\n"
            "👇 <i>Controlla hotel economici e prenota l'ingresso prioritario alle terme:</i>"
        )
    },
    {
        "id": "rimborso_volo_ritardo_cancellato",
        "title": "💶 Come ottenere fino a 600€ di risarcimento per volo in ritardo o cancellato (Regolamento CE 261/2004)",
        "destination": None,
        "amazon_query": "pesa valigia digitale bilancia portatile",
        "content": (
            "⚖️ <b>CONOSCI I TUOI DIRITTI DI PASSEGGERO?</b>\n\n"
            "Se hai volato negli ultimi 3 anni e hai subito un ritardo o una cancellazione, potresti avere diritto a un risarcimento in denaro contante!\n\n"
            "💰 <b>Gli importi previsti dalla legge europea:</b>\n"
            "• Tratte fino a 1.500 km (es. Milano - Barcellona): <b>250€</b>\n"
            "• Tratte tra 1.500 e 3.500 km: <b>400€</b>\n"
            "• Tratte oltre 3.500 km (voli intercontinentali): <b>600€</b>\n\n"
            "⚠️ <b>Cosa fare subito in aeroporto:</b>\n"
            "1. Conserva la carta d'imbarco e lo scontrino di eventuali pasti/bevande.\n"
            "2. Fatti rilasciare la dichiarazione scritta del motivo del ritardo al banco.\n"
            "3. Se il ritardo supera le 3 ore all'arrivo, hai diritto al rimborso monetario!"
        )
    },
    {
        "id": "giappone_low_cost_guida",
        "title": "🇯🇵 Come fare un viaggio in Giappone spendendo meno di quanto pensi",
        "destination": "Tokyo",
        "amazon_query": "adattatore presa giappone tipo A",
        "content": (
            "⛩️ <b>SFATIAMO UN MITO: IL GIAPPONE NON È COSTOSO!</b>\n\n"
            "Oggi lo Yen è a minimi storici rispetto all'Euro, rendendo il Giappone una delle mete più vantaggiose di sempre:\n\n"
            "🍜 <b>Mangiare da re con 6€-8€</b>: I Konbini (7-Eleven, Lawson, FamilyMart) e i ristoranti di Ramen / Soba con macchinetta automatica offrono cibo di altissima qualità a prezzi stracciati.\n"
            "🏨 <b>Business Hotel & Hotel a Capsule</b>: Hotel come APA o capsule di design offrono stanze pulitissime, wi-fi e set di cortesia a partire da 35€ a notte.\n"
            "🚇 <b>Spostamenti</b>: Le tessere prepagate Suica o Pasmo su iPhone/Android ti evitano sprechi di tempo e danno accesso a tutta la rete metropolitana.\n\n"
            "👇 <i>Pianifica il tuo viaggio da sogno con gli hotel e i tour consigliati:</i>"
        )
    },
    {
        "id": "segreti_booking_hotel",
        "title": "🏨 I trucchi per pagare gli Hotel fino al 40% in meno su Booking.com",
        "destination": None,
        "amazon_query": "organizer valigia set cubi compressione",
        "content": (
            "🔍 <b>COME RISPARMIARE SEMPRE SUGLI ALLOGGI</b>\n\n"
            "1️⃣ <b>Usa la navigazione da smartphone/app</b>: Molti hotel offrono una tariffa speciale 'Mobile Only' con uno sconto automatico del 10%-15% non visibile da PC desktop!\n"
            "2️⃣ <b>Attiva il livello Genius</b>: Già al livello 2 o 3 si sbloccano colazioni gratis, upgrade di stanza e sconti dal 10% al 20%.\n"
            "3️⃣ <b>Scegli sempre la 'Cancellazione Gratuita'</b>: Blocca subito la camera se il prezzo è buono. Se nelle settimane successive il prezzo scende o trovi un'offerta migliore, puoi cancellare con un click e riprenotare a meno!\n\n"
            "👇 <i>Fai una ricerca sulle mete più popolari con le migliori tariffe:</i>"
        )
    },
]


class GuideManager:
    def __init__(self, db: Database):
        self.db = db
        self.guides = TRAVEL_GUIDES

    def get_next_guide_to_publish(self) -> Optional[Dict[str, Any]]:
        """
        Selects a guide that has not been published recently (in the last 14 days).
        """
        available = [g for g in self.guides if not self.db.was_guide_recently_published(g["id"], days=7)]
        if not available:
            # If all were published recently, pick any random guide
            return random.choice(self.guides)
        return random.choice(available)

    def mark_published(self, guide: Dict[str, Any]):
        self.db.record_guide_published(
            guide_id=guide["id"],
            title=guide["title"],
            category="GUIDA DI VIAGGIO"
        )

    def get_all_guides(self) -> List[Dict[str, Any]]:
        return self.guides

    def get_guide_by_id(self, guide_id: str) -> Optional[Dict[str, Any]]:
        for g in self.guides:
            if g["id"] == guide_id:
                return g
        return None
