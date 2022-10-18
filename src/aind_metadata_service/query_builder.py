def subject_from_species_id(species_id):
    return (
        "SELECT "
        "  AC.SEX, "
        "  AC.COMPOSITE_PEDNUM, "
        "  AC.MATERNAL_NUMBER, "
        "  AC.MATERNAL_INDEX, "
        "  AC.PATERNAL_NUMBER, "
        "  AC.PATERNAL_INDEX, "
        "  AC.BIRTH_DATE, AC.ID, "
        "  AC.MOUSE_COMMENT, "
        "  S.SPECIES_NAME "
        "FROM ANIMALS_COMMON AC "
        "  LEFT OUTER JOIN SPECIES S ON AC.SPECIES_ID = S.ID "
        f"  WHERE AC.ID={species_id};"
    )
