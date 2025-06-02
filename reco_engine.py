def reco_engine_sfar(codes):
    reco = []

    # Étape 1 : chirurgie urgente
    if codes.get("C02") == "oui":
        reco.append("Chirurgie urgente : procéder sans examen complémentaire. Optimiser le traitement médical en péri-opératoire.")
        return reco

    # Risque opératoire
    risque = None
    for r in ["C03.1", "C03.2", "C03.3"]:
        if r in codes:
            risque = r
            break
    if not risque:
        return ["Information manquante : préciser le risque opératoire (faible, modéré, élevé)."]

    # Coronaropathie instable ?
    if "CV05.2" in codes:
        return ["Coronaropathie instable : retarder la chirurgie, initier un traitement spécifique et organiser une discussion collégiale."]
    elif "CV05.1" not in codes:
        return ["Information manquante : préciser si la coronaropathie est stable ou instable."]

    # Risque faible
    if risque == "C03.1":
        return ["Chirurgie à bas risque et coronaropathie stable : pas d’examen complémentaire nécessaire, chirurgie possible."]

    # Score de Lee
    if "CV02.1" not in codes:
        return ["Information manquante : indiquer le score de Lee."]
    lee = codes["CV02.1"]

    # Lee 0–1
    if lee <= 1:
        return ["Score de Lee 0–1 : chirurgie sans examen complémentaire."]

    # Lee = 2
    if lee == 2:
        if "C04" not in codes:
            return ["Information manquante : indiquer si la chirurgie est vasculaire."]
        if codes["C04"] == "non":
            return ["Score de Lee = 2 et chirurgie non vasculaire : pas d’examen complémentaire, chirurgie possible."]
        else:
            if not any(m in codes for m in ["CV03.1", "CV03.2", "CV03.3"]):
                return ["Information manquante : capacité fonctionnelle (METs)."]
            if "CV03.2" in codes:
                return ["Capacité fonctionnelle ≥ 4 MET : chirurgie sans examen complémentaire."]
            elif "CV03.1" in codes or "CV03.3" in codes:
                if not any(t in codes for t in ["X03.01", "X03.02", "X03.03"]):
                    return ["Information manquante : résultat du test d’ischémie."]
                if "X03.01" in codes:
                    return ["Test d’ischémie négatif : chirurgie possible."]
                elif "X03.02" in codes:
                    return ["Test d’ischémie positif : discuter une revascularisation préopératoire, optimiser le traitement médical et organiser une surveillance péri- et postopératoire rapprochée."]
                elif "X03.03" in codes:
                    return ["Test d’ischémie douteux : discuter en réunion collégiale et demander un avis spécialisé."]

    # Lee ≥ 3
    if lee >= 3:
        if not any(m in codes for m in ["CV03.1", "CV03.2", "CV03.3"]):
            return ["Information manquante : capacité fonctionnelle (METs)."]
        if "CV03.2" in codes:
            return ["Capacité fonctionnelle ≥ 4 MET : chirurgie sans examen complémentaire."]
        elif "CV03.1" in codes or "CV03.3" in codes:
            if not any(t in codes for t in ["X03.01", "X03.02", "X03.03"]):
                return ["Information manquante : résultat du test d’ischémie."]
            if "X03.01" in codes:
                return ["Test d’ischémie négatif : chirurgie possible."]
            elif "X03.02" in codes:
                return ["Test d’ischémie positif : discuter une revascularisation préopératoire, optimiser le traitement médical et organiser une surveillance péri- et postopératoire rapprochée."]
            elif "X03.03" in codes:
                return ["Test d’ischémie douteux : discuter en réunion collégiale et demander un avis spécialisé."]

    return reco
