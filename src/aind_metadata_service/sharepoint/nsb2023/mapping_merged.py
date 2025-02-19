class MappedNSBList:
    """Mapped Fields in Sharepoint list"""

    ISO_DUR_REGEX1 = re.compile(r"^ *(\d*\.?\d+)\s*(?:hour|hours)* *$")
    ISO_DUR_REGEX2 = re.compile(r"^(\d+):(\d+)$")
    ALT_TIME_REGEX = re.compile(
        r"^ *(7)(?:.0|/7|s on/7s off)? *(?:s|sec|secs|second|seconds)? *$"
    )
    INJ_ANGLE_REGEX = re.compile(
        r"^ *([-+]?\d*\.?\d+) *(?:deg|degree|degrees)* *$"
    )
    CURRENT_REGEX = re.compile(r"^ *([-+]?\d*\.?\d+) *(?:ua|uA|uAmp)* *$")
    LENGTH_OF_TIME_REGEX = re.compile(
        r"^ *(\d*\.?\d+) *(?:m|min|mins|minute|minutes)+ *$"
    )
    SCIENTIFIC_NOTATION_REGEX = re.compile(
        r"^[-+]?\d*\.?\d+[eE][-+]?\d+(?![\d.])"
    )
    CONCENTRATION_REGEX = re.compile(r"^\d+(\.\d+)?\s*mg[/]m[lL]$")
    LENGTH_MM_REGEX = re.compile(r"^([1-9]\.\d) mm$")

    def __init__(self, nsb: NSBList):
        """Class constructor"""
        self._nsb = nsb

    @staticmethod
    def _map_float_to_decimal(value: Optional[float]) -> Optional[Decimal]:
        """Parse string representation of float such as '0.25'."""
        return None if value is None else Decimal(str(value))

    @staticmethod
    def _parse_basic_decimal_str(value: Optional[str]) -> Optional[Decimal]:
        """Parse string representation of decimal such as '0.25'."""
        try:
            return None if value is None else Decimal(value)
        except (ValueError, DecimalException):
            return None

    @staticmethod
    def _parse_basic_float_str(float_str: Optional[str]) -> Optional[float]:
        """Parse string representation of float such as '0.25'."""
        try:
            return None if float_str is None else float(float_str)
        except ValueError:
            return None

    def _parse_current_str(self, cur_str: Optional[str]) -> Optional[Decimal]:
        """Parse current strings"""
        if cur_str is not None:
            parsed_string = re.search(self.CURRENT_REGEX, cur_str)
            if parsed_string is not None:
                return self._parse_basic_decimal_str(parsed_string.group(1))
            else:
                return None
        else:
            return None

    def _parse_length_of_time_str(
        self, len_of_time_str: Optional[str]
    ) -> Optional[Decimal]:
        """Parse length of time strings"""
        if len_of_time_str is not None:
            parsed_string = re.search(
                self.LENGTH_OF_TIME_REGEX, len_of_time_str
            )
            if parsed_string is not None:
                return self._parse_basic_decimal_str(parsed_string.group(1))
            else:
                return None
        else:
            return None

    def _parse_fiber_length_mm_str(self, fiber_length_str: Optional[str]):
        """Parses length of fiber length strings"""
        if fiber_length_str is not None:
            parsed_string = re.search(self.LENGTH_MM_REGEX, fiber_length_str)
            if parsed_string:
                return self._parse_basic_decimal_str(parsed_string.group(1))
            else:
                return None
        else:
            return None

    @staticmethod
    def _parse_datetime_to_date(dt: Optional[datetime]) -> Optional[date]:
        """Parse date from datetime"""
        return None if dt is None else dt.date()

    @staticmethod
    def _parse_virus_strain_str(
        virus_strain_str: Optional[str],
    ) -> Optional[str]:
        """Parse virus strain strings"""
        # TODO: Figure out how to parse virus strain field
        return virus_strain_str

    def _is_titer(self, titer_str: str) -> bool:
        """Checks whether titer field is in scientific notation."""
        return bool(re.search(self.SCIENTIFIC_NOTATION_REGEX, titer_str))

    def _is_concentration(self, titer_str: str) -> bool:
        """Checks whether titer field contains concentration."""
        return bool(re.search(self.CONCENTRATION_REGEX, titer_str))

    @staticmethod
    def _parse_titer_str(titer_str: Optional[str]) -> Optional[int]:
        """Parse string representation of titer into int."""
        return None if titer_str is None else int(float(titer_str))

    @staticmethod
    def _parse_concentration_str(
        con_str: Optional[str],
    ) -> Optional[Decimal]:
        """Parse string representation of concentration into Decimal."""
        return None if con_str is None else Decimal(str(float(con_str)))

    @property
    def aind_age_at_injection(self) -> Optional[Decimal]:
        """Maps age_at_injection to aind model"""
        return self._parse_basic_decimal_str(self._nsb.age_at_injection)

    @property
    def aind_ap2nd_inj(self) -> Optional[Decimal]:
        """Maps ap2nd_inj to aind model"""
        return self._map_float_to_decimal(self._nsb.ap2nd_inj)

    @property
    def aind_author_id(self) -> Optional[int]:
        """Maps author_id to aind model"""
        return self._nsb.author_id

    @property
    def aind_behavior(self) -> Optional[Any]:
        """Maps behavior to aind model"""
        return (
            None
            if self._nsb.behavior is None
            else {
                self._nsb.behavior.NO: None,
                self._nsb.behavior.YES: None,
            }.get(self._nsb.behavior, None)
        )

    @property
    def aind_behavior_complete(self) -> Optional[datetime]:
        """Maps behavior_complete to aind model"""
        return self._nsb.behavior_complete

    @property
    def aind_behavior_type(self) -> Optional[Any]:
        """Maps behavior_type to aind model"""
        return (
            None
            if self._nsb.behavior_type is None
            else {
                self._nsb.behavior_type.SELECT: None,
                self._nsb.behavior_type.HABITUATION_ONLY: None,
                self._nsb.behavior_type.HABITUATION_PASSIVE_TRAIN: None,
                self._nsb.behavior_type.CHANGE_DETECTION_TASK: None,
                self._nsb.behavior_type.DR_AUDITORY_VISUAL_TASK: None,
                self._nsb.behavior_type.AIND_FORAGING_TASK_WITH_O: None,
                self._nsb.behavior_type.AIBS_CHARACTERIZATION_ROT: None,
                self._nsb.behavior_type.AIND_MOTOR_OBSERVATORY_WH: None,
            }.get(self._nsb.behavior_type, None)
        )

    @property
    def aind_breg2_lamb(self) -> Optional[Decimal]:
        """Maps breg2_lamb to aind model"""
        return self._map_float_to_decimal(self._nsb.breg2_lamb)

    @property
    def aind_burr1_injection_devi(self) -> Optional[Any]:
        """Maps burr1_injection_devi to aind model"""
        return (
            None
            if self._nsb.burr1_injection_devi is None
            else {
                self._nsb.burr1_injection_devi.SELECT: None,
                self._nsb.burr1_injection_devi.NANO_1: None,
                self._nsb.burr1_injection_devi.IONTO_1: None,
                self._nsb.burr1_injection_devi.NANO_2: None,
                self._nsb.burr1_injection_devi.IONTO_2: None,
                self._nsb.burr1_injection_devi.NANO_3: None,
                self._nsb.burr1_injection_devi.IONTO_3: None,
                self._nsb.burr1_injection_devi.NANO_4: None,
                self._nsb.burr1_injection_devi.IONTO_4: None,
                self._nsb.burr1_injection_devi.NANO_5: None,
                self._nsb.burr1_injection_devi.IONTO_5: None,
                self._nsb.burr1_injection_devi.NANO_6: None,
                self._nsb.burr1_injection_devi.IONTO_6: None,
                self._nsb.burr1_injection_devi.NANO_7: None,
                self._nsb.burr1_injection_devi.IONTO_7: None,
                self._nsb.burr1_injection_devi.NANO_8: None,
                self._nsb.burr1_injection_devi.IONTO_8: None,
                self._nsb.burr1_injection_devi.NANO_9: None,
                self._nsb.burr1_injection_devi.IONTO_9: None,
            }.get(self._nsb.burr1_injection_devi, None)
        )

    @property
    def aind_burr1_perform_during(self) -> Optional[During]:
        """Maps burr1_perform_during to aind model"""
        return (
            None
            if self._nsb.burr1_perform_during is None
            else {
                self._nsb.burr1_perform_during.INITIAL_SURGERY: During.INITIAL,
                self._nsb.burr1_perform_during.FOLLOW_UP_SURGERY: During.FOLLOW_UP,
            }.get(self._nsb.burr1_perform_during, None)
        )

    @property
    def aind_burr1_virus_biosafte(self) -> Optional[Any]:
        """Maps burr1_virus_biosafte to aind model"""
        return (
            None
            if self._nsb.burr1_virus_biosafte is None
            else {
                self._nsb.burr1_virus_biosafte.SELECT: None,
                self._nsb.burr1_virus_biosafte.BSL_1_AAV: None,
                self._nsb.burr1_virus_biosafte.BSL_1_BEADS: None,
                self._nsb.burr1_virus_biosafte.BSL_1_AAV_BEADS: None,
                self._nsb.burr1_virus_biosafte.BSL_1_OTHER_WRITE_IN_COMM: None,
                self._nsb.burr1_virus_biosafte.BSL_2_RABIES: None,
                self._nsb.burr1_virus_biosafte.BSL_2_CAV: None,
                self._nsb.burr1_virus_biosafte.BSL_2_6OHDA: None,
                self._nsb.burr1_virus_biosafte.BSL_2_SINDBIS: None,
                self._nsb.burr1_virus_biosafte.BSL_2_HSV1: None,
                self._nsb.burr1_virus_biosafte.BSL_2_LENTI: None,
                self._nsb.burr1_virus_biosafte.BSL_2_CHOLERA_TOXIN_B: None,
                self._nsb.burr1_virus_biosafte.BSL_2_OTHER_WRITE_IN_COMM: None,
            }.get(self._nsb.burr1_virus_biosafte, None)
        )

    @property
    def aind_burr2_injection_devi(self) -> Optional[Any]:
        """Maps burr2_injection_devi to aind model"""
        return (
            None
            if self._nsb.burr2_injection_devi is None
            else {
                self._nsb.burr2_injection_devi.SELECT: None,
                self._nsb.burr2_injection_devi.NANO_1: None,
                self._nsb.burr2_injection_devi.IONTO_1: None,
                self._nsb.burr2_injection_devi.NANO_2: None,
                self._nsb.burr2_injection_devi.IONTO_2: None,
                self._nsb.burr2_injection_devi.NANO_3: None,
                self._nsb.burr2_injection_devi.IONTO_3: None,
                self._nsb.burr2_injection_devi.NANO_4: None,
                self._nsb.burr2_injection_devi.IONTO_4: None,
                self._nsb.burr2_injection_devi.NANO_5: None,
                self._nsb.burr2_injection_devi.IONTO_5: None,
                self._nsb.burr2_injection_devi.NANO_6: None,
                self._nsb.burr2_injection_devi.IONTO_6: None,
                self._nsb.burr2_injection_devi.NANO_7: None,
                self._nsb.burr2_injection_devi.IONTO_7: None,
                self._nsb.burr2_injection_devi.NANO_8: None,
                self._nsb.burr2_injection_devi.IONTO_8: None,
                self._nsb.burr2_injection_devi.NANO_9: None,
                self._nsb.burr2_injection_devi.IONTO_9: None,
            }.get(self._nsb.burr2_injection_devi, None)
        )

    @property
    def aind_burr2_perform_during(self) -> Optional[During]:
        """Maps burr2_perform_during to aind model"""
        return (
            None
            if self._nsb.burr2_perform_during is None
            else {
                self._nsb.burr2_perform_during.INITIAL_SURGERY: During.INITIAL,
                self._nsb.burr2_perform_during.FOLLOW_UP_SURGERY: During.FOLLOW_UP,
            }.get(self._nsb.burr2_perform_during, None)
        )

    @property
    def aind_burr2_status(self) -> Optional[Any]:
        """Maps burr2_status to aind model"""
        return (
            None
            if self._nsb.burr2_status is None
            else {
                self._nsb.burr2_status.COMPLETE: None,
            }.get(self._nsb.burr2_status, None)
        )

    @property
    def aind_burr2_virus_biosafte(self) -> Optional[Any]:
        """Maps burr2_virus_biosafte to aind model"""
        return (
            None
            if self._nsb.burr2_virus_biosafte is None
            else {
                self._nsb.burr2_virus_biosafte.SELECT: None,
                self._nsb.burr2_virus_biosafte.BSL_1_AAV: None,
                self._nsb.burr2_virus_biosafte.BSL_1_BEADS: None,
                self._nsb.burr2_virus_biosafte.BSL_1_AAV_BEADS: None,
                self._nsb.burr2_virus_biosafte.BSL_1_OTHER_WRITE_IN_COMM: None,
                self._nsb.burr2_virus_biosafte.BSL_2_RABIES: None,
                self._nsb.burr2_virus_biosafte.BSL_2_CAV: None,
                self._nsb.burr2_virus_biosafte.BSL_2_6OHDA: None,
                self._nsb.burr2_virus_biosafte.BSL_2_SINDBIS: None,
                self._nsb.burr2_virus_biosafte.BSL_2_HSV1: None,
                self._nsb.burr2_virus_biosafte.BSL_2_LENTI: None,
                self._nsb.burr2_virus_biosafte.BSL_2_CHOLERA_TOXIN_B: None,
                self._nsb.burr2_virus_biosafte.BSL_2_OTHER_WRITE_IN_COMM: None,
            }.get(self._nsb.burr2_virus_biosafte, None)
        )

    @property
    def aind_burr3_a_p(self) -> Optional[Decimal]:
        """Maps burr3_a_p to aind model"""
        return self._map_float_to_decimal(self._nsb.burr3_a_p)

    @property
    def aind_burr3_d_v(self) -> Optional[Decimal]:
        """Maps burr3_d_v to aind model"""
        return self._map_float_to_decimal(self._nsb.burr3_d_v)

    @property
    def aind_burr3_injection_devi(self) -> Optional[Any]:
        """Maps burr3_injection_devi to aind model"""
        return (
            None
            if self._nsb.burr3_injection_devi is None
            else {
                self._nsb.burr3_injection_devi.SELECT: None,
                self._nsb.burr3_injection_devi.NANO_1: None,
                self._nsb.burr3_injection_devi.IONTO_1: None,
                self._nsb.burr3_injection_devi.NANO_2: None,
                self._nsb.burr3_injection_devi.IONTO_2: None,
                self._nsb.burr3_injection_devi.NANO_3: None,
                self._nsb.burr3_injection_devi.IONTO_3: None,
                self._nsb.burr3_injection_devi.NANO_4: None,
                self._nsb.burr3_injection_devi.IONTO_4: None,
                self._nsb.burr3_injection_devi.NANO_5: None,
                self._nsb.burr3_injection_devi.IONTO_5: None,
                self._nsb.burr3_injection_devi.NANO_6: None,
                self._nsb.burr3_injection_devi.IONTO_6: None,
                self._nsb.burr3_injection_devi.NANO_7: None,
                self._nsb.burr3_injection_devi.IONTO_7: None,
                self._nsb.burr3_injection_devi.NANO_8: None,
                self._nsb.burr3_injection_devi.IONTO_8: None,
                self._nsb.burr3_injection_devi.NANO_9: None,
                self._nsb.burr3_injection_devi.IONTO_9: None,
            }.get(self._nsb.burr3_injection_devi, None)
        )

    @property
    def aind_burr3_m_l(self) -> Optional[Decimal]:
        """Maps burr3_m_l to aind model"""
        return self._map_float_to_decimal(self._nsb.burr3_m_l)

    @property
    def aind_burr3_perform_during(self) -> Optional[During]:
        """Maps burr3_perform_during to aind model"""
        return (
            None
            if self._nsb.burr3_perform_during is None
            else {
                self._nsb.burr3_perform_during.INITIAL_SURGERY: During.INITIAL,
                self._nsb.burr3_perform_during.FOLLOW_UP_SURGERY: During.FOLLOW_UP,
            }.get(self._nsb.burr3_perform_during, None)
        )

    @property
    def aind_burr3_status(self) -> Optional[Any]:
        """Maps burr3_status to aind model"""
        return (
            None
            if self._nsb.burr3_status is None
            else {
                self._nsb.burr3_status.COMPLETE: None,
            }.get(self._nsb.burr3_status, None)
        )

    @property
    def aind_burr3_virus_biosafet(self) -> Optional[Any]:
        """Maps burr3_virus_biosafet to aind model"""
        return (
            None
            if self._nsb.burr3_virus_biosafet is None
            else {
                self._nsb.burr3_virus_biosafet.SELECT: None,
                self._nsb.burr3_virus_biosafet.BSL_1_AAV: None,
                self._nsb.burr3_virus_biosafet.BSL_1_BEADS: None,
                self._nsb.burr3_virus_biosafet.BSL_1_AAV_BEADS: None,
                self._nsb.burr3_virus_biosafet.BSL_1_OTHER_WRITE_IN_COMM: None,
                self._nsb.burr3_virus_biosafet.BSL_2_RABIES: None,
                self._nsb.burr3_virus_biosafet.BSL_2_CAV: None,
                self._nsb.burr3_virus_biosafet.BSL_2_6OHDA: None,
                self._nsb.burr3_virus_biosafet.BSL_2_SINDBIS: None,
                self._nsb.burr3_virus_biosafet.BSL_2_HSV1: None,
                self._nsb.burr3_virus_biosafet.BSL_2_LENTI: None,
                self._nsb.burr3_virus_biosafet.BSL_2_CHOLERA_TOXIN_B: None,
                self._nsb.burr3_virus_biosafet.BSL_2_OTHER_WRITE_IN_COMM: None,
            }.get(self._nsb.burr3_virus_biosafet, None)
        )

    @property
    def aind_burr4_a_p(self) -> Optional[Decimal]:
        """Maps burr4_a_p to aind model"""
        return self._map_float_to_decimal(self._nsb.burr4_a_p)

    @property
    def aind_burr4_d_v(self) -> Optional[Decimal]:
        """Maps burr4_d_v to aind model"""
        return self._map_float_to_decimal(self._nsb.burr4_d_v)

    @property
    def aind_burr4_injection_devi(self) -> Optional[Any]:
        """Maps burr4_injection_devi to aind model"""
        return (
            None
            if self._nsb.burr4_injection_devi is None
            else {
                self._nsb.burr4_injection_devi.SELECT: None,
                self._nsb.burr4_injection_devi.NANO_1: None,
                self._nsb.burr4_injection_devi.IONTO_1: None,
                self._nsb.burr4_injection_devi.NANO_2: None,
                self._nsb.burr4_injection_devi.IONTO_2: None,
                self._nsb.burr4_injection_devi.NANO_3: None,
                self._nsb.burr4_injection_devi.IONTO_3: None,
                self._nsb.burr4_injection_devi.NANO_4: None,
                self._nsb.burr4_injection_devi.IONTO_4: None,
                self._nsb.burr4_injection_devi.NANO_5: None,
                self._nsb.burr4_injection_devi.IONTO_5: None,
                self._nsb.burr4_injection_devi.NANO_6: None,
                self._nsb.burr4_injection_devi.IONTO_6: None,
                self._nsb.burr4_injection_devi.NANO_7: None,
                self._nsb.burr4_injection_devi.IONTO_7: None,
                self._nsb.burr4_injection_devi.NANO_8: None,
                self._nsb.burr4_injection_devi.IONTO_8: None,
                self._nsb.burr4_injection_devi.IONTO_9: None,
            }.get(self._nsb.burr4_injection_devi, None)
        )

    @property
    def aind_burr4_m_l(self) -> Optional[Decimal]:
        """Maps burr4_m_l to aind model"""
        return self._map_float_to_decimal(self._nsb.burr4_m_l)

    @property
    def aind_burr4_perform_during(self) -> Optional[During]:
        """Maps burr4_perform_during to aind model"""
        return (
            None
            if self._nsb.burr4_perform_during is None
            else {
                self._nsb.burr4_perform_during.INITIAL_SURGERY: During.INITIAL,
                self._nsb.burr4_perform_during.FOLLOW_UP_SURGERY: During.FOLLOW_UP,
            }.get(self._nsb.burr4_perform_during, None)
        )

    @property
    def aind_burr4_status(self) -> Optional[Any]:
        """Maps burr4_status to aind model"""
        return (
            None
            if self._nsb.burr4_status is None
            else {
                self._nsb.burr4_status.COMPLETE: None,
            }.get(self._nsb.burr4_status, None)
        )

    @property
    def aind_burr4_virus_biosafte(self) -> Optional[Any]:
        """Maps burr4_virus_biosafte to aind model"""
        return (
            None
            if self._nsb.burr4_virus_biosafte is None
            else {
                self._nsb.burr4_virus_biosafte.SELECT: None,
                self._nsb.burr4_virus_biosafte.BSL_1_AAV: None,
                self._nsb.burr4_virus_biosafte.BSL_1_BEADS: None,
                self._nsb.burr4_virus_biosafte.BSL_1_AAV_BEADS: None,
                self._nsb.burr4_virus_biosafte.BSL_1_OTHER_WRITE_IN_COMM: None,
                self._nsb.burr4_virus_biosafte.BSL_2_RABIES: None,
                self._nsb.burr4_virus_biosafte.BSL_2_CAV: None,
                self._nsb.burr4_virus_biosafte.BSL_2_6OHDA: None,
                self._nsb.burr4_virus_biosafte.BSL_2_SINDBIS: None,
                self._nsb.burr4_virus_biosafte.BSL_2_HSV1: None,
                self._nsb.burr4_virus_biosafte.BSL_2_LENTI: None,
                self._nsb.burr4_virus_biosafte.BSL_2_CHOLERA_TOXIN_B: None,
                self._nsb.burr4_virus_biosafte.BSL_2_OTHER_WRITE_IN_COMM: None,
            }.get(self._nsb.burr4_virus_biosafte, None)
        )

    @property
    def aind_burr5_injection_devi(self) -> Optional[Any]:
        """Maps burr5_injection_devi to aind model"""
        return (
            None
            if self._nsb.burr5_injection_devi is None
            else {
                self._nsb.burr5_injection_devi.SELECT: None,
                self._nsb.burr5_injection_devi.NANO_1: None,
                self._nsb.burr5_injection_devi.IONTO_1: None,
                self._nsb.burr5_injection_devi.NANO_2: None,
                self._nsb.burr5_injection_devi.IONTO_2: None,
                self._nsb.burr5_injection_devi.NANO_3: None,
                self._nsb.burr5_injection_devi.IONTO_3: None,
                self._nsb.burr5_injection_devi.NANO_4: None,
                self._nsb.burr5_injection_devi.IONTO_4: None,
                self._nsb.burr5_injection_devi.NANO_5: None,
                self._nsb.burr5_injection_devi.IONTO_5: None,
                self._nsb.burr5_injection_devi.NANO_6: None,
                self._nsb.burr5_injection_devi.IONTO_6: None,
                self._nsb.burr5_injection_devi.NANO_7: None,
                self._nsb.burr5_injection_devi.IONTO_7: None,
                self._nsb.burr5_injection_devi.NANO_8: None,
                self._nsb.burr5_injection_devi.IONTO_8: None,
                self._nsb.burr5_injection_devi.NANO_9: None,
                self._nsb.burr5_injection_devi.IONTO_9: None,
            }.get(self._nsb.burr5_injection_devi, None)
        )

    @property
    def aind_burr5_perform_during(self) -> Optional[During]:
        """Maps burr5_perform_during to aind model"""
        return (
            None
            if self._nsb.burr5_status is None
            else {
                self._nsb.burr5_perform_during.INITIAL_SURGERY: During.INITIAL,
                self._nsb.burr5_perform_during.FOLLOW_UP_SURGERY: During.FOLLOW_UP,
            }.get(self._nsb.burr5_perform_during, None)
        )

    @property
    def aind_burr5_status(self) -> Optional[Any]:
        """Maps burr5_status to aind model"""
        return (
            None
            if self._nsb.burr5_status is None
            else {
                self._nsb.burr5_status.COMPLETE: None,
            }.get(self._nsb.burr5_status, None)
        )

    @property
    def aind_burr5_virus_biosafte(self) -> Optional[Any]:
        """Maps burr5_virus_biosafte to aind model"""
        return (
            None
            if self._nsb.burr5_virus_biosafte is None
            else {
                self._nsb.burr5_virus_biosafte.SELECT: None,
                self._nsb.burr5_virus_biosafte.BSL_1_AAV: None,
                self._nsb.burr5_virus_biosafte.BSL_1_BEADS: None,
                self._nsb.burr5_virus_biosafte.BSL_1_AAV_BEADS: None,
                self._nsb.burr5_virus_biosafte.BSL_1_OTHER_WRITE_IN_COMM: None,
                self._nsb.burr5_virus_biosafte.BSL_2_RABIES: None,
                self._nsb.burr5_virus_biosafte.BSL_2_CAV: None,
                self._nsb.burr5_virus_biosafte.BSL_2_6OHDA: None,
                self._nsb.burr5_virus_biosafte.BSL_2_SINDBIS: None,
                self._nsb.burr5_virus_biosafte.BSL_2_HSV1: None,
                self._nsb.burr5_virus_biosafte.BSL_2_LENTI: None,
                self._nsb.burr5_virus_biosafte.BSL_2_CHOLERA_TOXIN_B: None,
                self._nsb.burr5_virus_biosafte.BSL_2_OTHER_WRITE_IN_COMM: None,
            }.get(self._nsb.burr5_virus_biosafte, None)
        )

    @property
    def aind_burr6_injection_devi(self) -> Optional[Any]:
        """Maps burr6_injection_devi to aind model"""
        return (
            None
            if self._nsb.burr6_injection_devi is None
            else {
                self._nsb.burr6_injection_devi.SELECT: None,
                self._nsb.burr6_injection_devi.NANO_1: None,
                self._nsb.burr6_injection_devi.IONTO_1: None,
                self._nsb.burr6_injection_devi.NANO_2: None,
                self._nsb.burr6_injection_devi.IONTO_2: None,
                self._nsb.burr6_injection_devi.NANO_3: None,
                self._nsb.burr6_injection_devi.IONTO_3: None,
                self._nsb.burr6_injection_devi.NANO_4: None,
                self._nsb.burr6_injection_devi.IONTO_4: None,
                self._nsb.burr6_injection_devi.NANO_5: None,
                self._nsb.burr6_injection_devi.IONTO_5: None,
                self._nsb.burr6_injection_devi.NANO_6: None,
                self._nsb.burr6_injection_devi.IONTO_6: None,
                self._nsb.burr6_injection_devi.NANO_7: None,
                self._nsb.burr6_injection_devi.IONTO_7: None,
                self._nsb.burr6_injection_devi.NANO_8: None,
                self._nsb.burr6_injection_devi.IONTO_8: None,
                self._nsb.burr6_injection_devi.NANO_9: None,
                self._nsb.burr6_injection_devi.IONTO_9: None,
            }.get(self._nsb.burr6_injection_devi, None)
        )

    @property
    def aind_burr6_perform_during(self) -> Optional[During]:
        """Maps burr6_perform_during to aind model"""
        return (
            None
            if self._nsb.burr6_perform_during is None
            else {
                self._nsb.burr6_perform_during.INITIAL_SURGERY: During.INITIAL,
                self._nsb.burr6_perform_during.FOLLOW_UP_SURGERY: During.FOLLOW_UP,
            }.get(self._nsb.burr6_perform_during, None)
        )

    @property
    def aind_burr6_status(self) -> Optional[Any]:
        """Maps burr6_status to aind model"""
        return (
            None
            if self._nsb.burr6_status is None
            else {
                self._nsb.burr6_status.COMPLETE: None,
            }.get(self._nsb.burr6_status, None)
        )

    @property
    def aind_burr6_virus_biosafte(self) -> Optional[Any]:
        """Maps burr6_virus_biosafte to aind model"""
        return (
            None
            if self._nsb.burr6_virus_biosafte is None
            else {
                self._nsb.burr6_virus_biosafte.SELECT: None,
                self._nsb.burr6_virus_biosafte.BSL_1_AAV: None,
                self._nsb.burr6_virus_biosafte.BSL_1_BEADS: None,
                self._nsb.burr6_virus_biosafte.BSL_1_AAV_BEADS: None,
                self._nsb.burr6_virus_biosafte.BSL_1_OTHER_WRITE_IN_COMM: None,
                self._nsb.burr6_virus_biosafte.BSL_2_RABIES: None,
                self._nsb.burr6_virus_biosafte.BSL_2_CAV: None,
                self._nsb.burr6_virus_biosafte.BSL_2_6OHDA: None,
                self._nsb.burr6_virus_biosafte.BSL_2_SINDBIS: None,
                self._nsb.burr6_virus_biosafte.BSL_2_HSV1: None,
                self._nsb.burr6_virus_biosafte.BSL_2_LENTI: None,
                self._nsb.burr6_virus_biosafte.BSL_2_CHOLERA_TOXIN_B: None,
                self._nsb.burr6_virus_biosafte.BSL_2_OTHER_WRITE_IN_COMM: None,
            }.get(self._nsb.burr6_virus_biosafte, None)
        )

    @property
    def aind_burr_1_d_v_x00(self) -> Optional[Decimal]:
        """Maps burr_1_d_v_x00 to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_1_d_v_x00)

    @property
    def aind_burr_1_dv_2(self) -> Optional[Decimal]:
        """Maps burr_1_dv_2 to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_1_dv_2)

    @property
    def aind_burr_1_fiber_t(self) -> Optional[FiberType]:
        """Maps burr_1_fiber_t to aind model"""
        return (
            None
            if self._nsb.burr_1_fiber_t is None
            else {
                self._nsb.burr_1_fiber_t.STANDARD_PROVIDED_BY_NSB: FiberType.STANDARD,
                self._nsb.burr_1_fiber_t.CUSTOM: FiberType.CUSTOM,
            }.get(self._nsb.burr_1_fiber_t, None)
        )

    @property
    def aind_burr_1_injectable_x0(self) -> Optional[str]:
        """Maps burr_1_injectable_x0 to aind model"""
        # TODO: figure out how to parse injectable materials
        # first 4 are injectable material, other 4 are titer
        return self._nsb.burr_1_injectable_x0

    @property
    def aind_burr_1_injectable_x00(self) -> Optional[str]:
        """Maps burr_1_injectable_x00 to aind model"""
        return self._nsb.burr_1_injectable_x00

    @property
    def aind_burr_1_injectable_x01(self) -> Optional[str]:
        """Maps burr_1_injectable_x01 to aind model"""
        return self._nsb.burr_1_injectable_x01

    @property
    def aind_burr_1_injectable_x02(self) -> Optional[str]:
        """Maps burr_1_injectable_x02 to aind model"""
        return self._nsb.burr_1_injectable_x02

    @property
    def aind_burr_1_injectable_x03(self) -> Optional[str]:
        """Maps burr_1_injectable_x03 to aind model"""
        return self._nsb.burr_1_injectable_x03

    @property
    def aind_burr_1_injectable_x04(self) -> Optional[str]:
        """Maps burr_1_injectable_x04 to aind model"""
        return self._nsb.burr_1_injectable_x04

    @property
    def aind_burr_1_injectable_x05(self) -> Optional[str]:
        """Maps burr_1_injectable_x05 to aind model"""
        return self._nsb.burr_1_injectable_x05

    @property
    def aind_burr_1_injectable_x06(self) -> Optional[str]:
        """Maps burr_1_injectable_x06 to aind model"""
        return self._nsb.burr_1_injectable_x06

    @property
    def aind_burr_2_d_v_x00(self) -> Optional[Decimal]:
        """Maps burr_2_d_v_x00 to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_2_d_v_x00)

    @property
    def aind_burr_2_d_v_x000(self) -> Optional[Decimal]:
        """Maps burr_2_d_v_x000 to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_2_d_v_x000)

    @property
    def aind_burr_2_fiber_t(self) -> Optional[FiberType]:
        """Maps burr_2_fiber_t to aind model"""
        return (
            None
            if self._nsb.burr_2_fiber_t is None
            else {
                self._nsb.burr_2_fiber_t.STANDARD_PROVIDED_BY_NSB: FiberType.STANDARD,
                self._nsb.burr_2_fiber_t.CUSTOM: FiberType.CUSTOM,
            }.get(self._nsb.burr_2_fiber_t, None)
        )

    @property
    def aind_burr_2_injectable_x0(self) -> Optional[str]:
        """Maps burr_2_injectable_x0 to aind model"""
        return self._nsb.burr_2_injectable_x0

    @property
    def aind_burr_2_injectable_x00(self) -> Optional[str]:
        """Maps burr_2_injectable_x00 to aind model"""
        return self._nsb.burr_2_injectable_x00

    @property
    def aind_burr_2_injectable_x01(self) -> Optional[str]:
        """Maps burr_2_injectable_x01 to aind model"""
        return self._nsb.burr_2_injectable_x01

    @property
    def aind_burr_2_injectable_x02(self) -> Optional[str]:
        """Maps burr_2_injectable_x02 to aind model"""
        return self._nsb.burr_2_injectable_x02

    @property
    def aind_burr_2_injectable_x03(self) -> Optional[str]:
        """Maps burr_2_injectable_x03 to aind model"""
        return self._nsb.burr_2_injectable_x03

    @property
    def aind_burr_2_injectable_x04(self) -> Optional[str]:
        """Maps burr_2_injectable_x04 to aind model"""
        return self._nsb.burr_2_injectable_x04

    @property
    def aind_burr_2_injectable_x05(self) -> Optional[str]:
        """Maps burr_2_injectable_x05 to aind model"""
        return self._nsb.burr_2_injectable_x05

    @property
    def aind_burr_2_injectable_x06(self) -> Optional[str]:
        """Maps burr_2_injectable_x06 to aind model"""
        return self._nsb.burr_2_injectable_x06

    @property
    def aind_burr_3_angle(self) -> Optional[Decimal]:
        """Maps burr_3_angle to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_3_angle)

    @property
    def aind_burr_3_d_v_x00(self) -> Optional[Decimal]:
        """Maps burr_3_d_v_x00 to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_3_d_v_x00)

    @property
    def aind_burr_3_d_v_x000(self) -> Optional[Decimal]:
        """Maps burr_3_d_v_x000 to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_3_d_v_x000)

    @property
    def aind_burr_3_fiber_t(self) -> Optional[FiberType]:
        """Maps burr_3_fiber_t to aind model"""
        return (
            None
            if self._nsb.burr_3_fiber_t is None
            else {
                self._nsb.burr_3_fiber_t.STANDARD_PROVIDED_BY_NSB: FiberType.STANDARD,
                self._nsb.burr_3_fiber_t.CUSTOM: FiberType.CUSTOM,
            }.get(self._nsb.burr_3_fiber_t, None)
        )

    @property
    def aind_burr_3_hemisphere(self) -> Optional[Side]:
        """Maps burr_3_hemisphere to aind model"""
        return (
            None
            if self._nsb.burr_3_hemisphere is None
            else {
                self._nsb.burr_3_hemisphere.SELECT: None,
                self._nsb.burr_3_hemisphere.LEFT: Side.LEFT,
                self._nsb.burr_3_hemisphere.RIGHT: Side.RIGHT,
            }.get(self._nsb.burr_3_hemisphere, None)
        )

    @property
    def aind_burr_3_injectable_x0(self) -> Optional[str]:
        """Maps burr_3_injectable_x0 to aind model"""
        return self._nsb.burr_3_injectable_x0

    @property
    def aind_burr_3_injectable_x00(self) -> Optional[str]:
        """Maps burr_3_injectable_x00 to aind model"""
        return self._nsb.burr_3_injectable_x00

    @property
    def aind_burr_3_injectable_x01(self) -> Optional[str]:
        """Maps burr_3_injectable_x01 to aind model"""
        return self._nsb.burr_3_injectable_x01

    @property
    def aind_burr_3_injectable_x02(self) -> Optional[str]:
        """Maps burr_3_injectable_x02 to aind model"""
        return self._nsb.burr_3_injectable_x02

    @property
    def aind_burr_3_injectable_x03(self) -> Optional[str]:
        """Maps burr_3_injectable_x03 to aind model"""
        return self._nsb.burr_3_injectable_x03

    @property
    def aind_burr_3_injectable_x04(self) -> Optional[str]:
        """Maps burr_3_injectable_x04 to aind model"""
        return self._nsb.burr_3_injectable_x04

    @property
    def aind_burr_3_injectable_x05(self) -> Optional[str]:
        """Maps burr_3_injectable_x05 to aind model"""
        return self._nsb.burr_3_injectable_x05

    @property
    def aind_burr_3_injectable_x06(self) -> Optional[str]:
        """Maps burr_3_injectable_x06 to aind model"""
        return self._nsb.burr_3_injectable_x06

    @property
    def aind_burr_4_angle(self) -> Optional[Decimal]:
        """Maps burr_4_angle to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_4_angle)

    @property
    def aind_burr_4_d_v_x00(self) -> Optional[Decimal]:
        """Maps burr_4_d_v_x00 to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_4_d_v_x00)

    @property
    def aind_burr_4_d_v_x000(self) -> Optional[Decimal]:
        """Maps burr_4_d_v_x000 to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_4_d_v_x000)

    @property
    def aind_burr_4_fiber_t(self) -> Optional[FiberType]:
        """Maps burr_4_fiber_t to aind model"""
        return (
            None
            if self._nsb.burr_4_fiber_t is None
            else {
                self._nsb.burr_4_fiber_t.STANDARD_PROVIDED_BY_NSB: FiberType.STANDARD,
                self._nsb.burr_4_fiber_t.CUSTOM: FiberType.CUSTOM,
            }.get(self._nsb.burr_4_fiber_t, None)
        )

    @property
    def aind_burr_4_hemisphere(self) -> Optional[Side]:
        """Maps burr_4_hemisphere to aind model"""
        return (
            None
            if self._nsb.burr_4_hemisphere is None
            else {
                self._nsb.burr_4_hemisphere.SELECT: None,
                self._nsb.burr_4_hemisphere.LEFT: Side.LEFT,
                self._nsb.burr_4_hemisphere.RIGHT: Side.RIGHT,
            }.get(self._nsb.burr_4_hemisphere, None)
        )

    @property
    def aind_burr_4_injectable_x0(self) -> Optional[str]:
        """Maps burr_4_injectable_x0 to aind model"""
        return self._nsb.burr_4_injectable_x0

    @property
    def aind_burr_4_injectable_x00(self) -> Optional[str]:
        """Maps burr_4_injectable_x00 to aind model"""
        return self._nsb.burr_4_injectable_x00

    @property
    def aind_burr_4_injectable_x01(self) -> Optional[str]:
        """Maps burr_4_injectable_x01 to aind model"""
        return self._nsb.burr_4_injectable_x01

    @property
    def aind_burr_4_injectable_x02(self) -> Optional[str]:
        """Maps burr_4_injectable_x02 to aind model"""
        return self._nsb.burr_4_injectable_x02

    @property
    def aind_burr_4_injectable_x03(self) -> Optional[str]:
        """Maps burr_4_injectable_x03 to aind model"""
        return self._nsb.burr_4_injectable_x03

    @property
    def aind_burr_4_injectable_x04(self) -> Optional[str]:
        """Maps burr_4_injectable_x04 to aind model"""
        return self._nsb.burr_4_injectable_x04

    @property
    def aind_burr_4_injectable_x05(self) -> Optional[str]:
        """Maps burr_4_injectable_x05 to aind model"""
        return self._nsb.burr_4_injectable_x05

    @property
    def aind_burr_4_injectable_x06(self) -> Optional[str]:
        """Maps burr_4_injectable_x06 to aind model"""
        return self._nsb.burr_4_injectable_x06

    @property
    def aind_burr_5_a_p(self) -> Optional[Decimal]:
        """Maps burr_5_a_p to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_5_a_p)

    @property
    def aind_burr_5_angle(self) -> Optional[Decimal]:
        """Maps burr_5_angle to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_5_angle)

    @property
    def aind_burr_5_d_v_x00(self) -> Optional[Decimal]:
        """Maps burr_5_d_v_x00 to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_5_d_v_x00)

    @property
    def aind_burr_5_d_v_x000(self) -> Optional[Decimal]:
        """Maps burr_5_d_v_x000 to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_5_d_v_x000)

    @property
    def aind_burr_5_d_v_x001(self) -> Optional[Decimal]:
        """Maps burr_5_d_v_x001 to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_5_d_v_x001)

    @property
    def aind_burr_5_fiber_t(self) -> Optional[Any]:
        """Maps burr_5_fiber_t to aind model"""
        return (
            None
            if self._nsb.burr_5_fiber_t is None
            else {
                self._nsb.burr_5_fiber_t.STANDARD_PROVIDED_BY_NSB: FiberType.STANDARD,
                self._nsb.burr_5_fiber_t.CUSTOM: FiberType.CUSTOM,
            }.get(self._nsb.burr_5_fiber_t, None)
        )

    @property
    def aind_burr_5_hemisphere(self) -> Optional[Side]:
        """Maps burr_5_hemisphere to aind model"""
        return (
            None
            if self._nsb.burr_5_hemisphere is None
            else {
                self._nsb.burr_5_hemisphere.SELECT: None,
                self._nsb.burr_5_hemisphere.LEFT: Side.LEFT,
                self._nsb.burr_5_hemisphere.RIGHT: Side.RIGHT,
            }.get(self._nsb.burr_5_hemisphere, None)
        )

    @property
    def aind_burr_5_injectable_x0(self) -> Optional[str]:
        """Maps burr_5_injectable_x0 to aind model"""
        return self._nsb.burr_5_injectable_x0

    @property
    def aind_burr_5_injectable_x00(self) -> Optional[str]:
        """Maps burr_5_injectable_x00 to aind model"""
        return self._nsb.burr_5_injectable_x00

    @property
    def aind_burr_5_injectable_x01(self) -> Optional[str]:
        """Maps burr_5_injectable_x01 to aind model"""
        return self._nsb.burr_5_injectable_x01

    @property
    def aind_burr_5_injectable_x02(self) -> Optional[str]:
        """Maps burr_5_injectable_x02 to aind model"""
        return self._nsb.burr_5_injectable_x02

    @property
    def aind_burr_5_injectable_x03(self) -> Optional[str]:
        """Maps burr_5_injectable_x03 to aind model"""
        return self._nsb.burr_5_injectable_x03

    @property
    def aind_burr_5_injectable_x04(self) -> Optional[str]:
        """Maps burr_5_injectable_x04 to aind model"""
        return self._nsb.burr_5_injectable_x04

    @property
    def aind_burr_5_injectable_x05(self) -> Optional[str]:
        """Maps burr_5_injectable_x05 to aind model"""
        return self._nsb.burr_5_injectable_x05

    @property
    def aind_burr_5_injectable_x06(self) -> Optional[str]:
        """Maps burr_5_injectable_x06 to aind model"""
        return self._nsb.burr_5_injectable_x06

    @property
    def aind_burr_5_m_l(self) -> Optional[Decimal]:
        """Maps burr_5_m_l to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_5_m_l)

    @property
    def aind_burr_6_a_p(self) -> Optional[Decimal]:
        """Maps burr_6_a_p to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_6_a_p)

    @property
    def aind_burr_6_angle(self) -> Optional[Decimal]:
        """Maps burr_6_angle to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_6_angle)

    @property
    def aind_burr_6_d_v_x00(self) -> Optional[Decimal]:
        """Maps burr_6_d_v_x00 to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_6_d_v_x00)

    @property
    def aind_burr_6_d_v_x000(self) -> Optional[Decimal]:
        """Maps burr_6_d_v_x000 to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_6_d_v_x000)

    @property
    def aind_burr_6_d_v_x001(self) -> Optional[Decimal]:
        """Maps burr_6_d_v_x001 to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_6_d_v_x001)

    @property
    def aind_burr_6_fiber_t(self) -> Optional[FiberType]:
        """Maps burr_6_fiber_t to aind model"""
        return (
            None
            if self._nsb.burr_6_fiber_t is None
            else {
                self._nsb.burr_6_fiber_t.STANDARD_PROVIDED_BY_NSB: FiberType.STANDARD,
                self._nsb.burr_6_fiber_t.CUSTOM: FiberType.CUSTOM,
            }.get(self._nsb.burr_6_fiber_t, None)
        )

    @property
    def aind_burr_6_hemisphere(self) -> Optional[Side]:
        """Maps burr_6_hemisphere to aind model"""
        return (
            None
            if self._nsb.burr_6_hemisphere is None
            else {
                self._nsb.burr_6_hemisphere.SELECT: None,
                self._nsb.burr_6_hemisphere.LEFT: Side.LEFT,
                self._nsb.burr_6_hemisphere.RIGHT: Side.RIGHT,
            }.get(self._nsb.burr_6_hemisphere, None)
        )

    @property
    def aind_burr_6_injectable_x0(self) -> Optional[str]:
        """Maps burr_6_injectable_x0 to aind model"""
        return self._nsb.burr_6_injectable_x0

    @property
    def aind_burr_6_injectable_x00(self) -> Optional[str]:
        """Maps burr_6_injectable_x00 to aind model"""
        return self._nsb.burr_6_injectable_x00

    @property
    def aind_burr_6_injectable_x01(self) -> Optional[str]:
        """Maps burr_6_injectable_x01 to aind model"""
        return self._nsb.burr_6_injectable_x01

    @property
    def aind_burr_6_injectable_x02(self) -> Optional[str]:
        """Maps burr_6_injectable_x02 to aind model"""
        return self._nsb.burr_6_injectable_x02

    @property
    def aind_burr_6_injectable_x03(self) -> Optional[str]:
        """Maps burr_6_injectable_x03 to aind model"""
        return self._nsb.burr_6_injectable_x03

    @property
    def aind_burr_6_injectable_x04(self) -> Optional[str]:
        """Maps burr_6_injectable_x04 to aind model"""
        return self._nsb.burr_6_injectable_x04

    @property
    def aind_burr_6_injectable_x05(self) -> Optional[str]:
        """Maps burr_6_injectable_x05 to aind model"""
        return self._nsb.burr_6_injectable_x05

    @property
    def aind_burr_6_injectable_x06(self) -> Optional[str]:
        """Maps burr_6_injectable_x06 to aind model"""
        return self._nsb.burr_6_injectable_x06

    @property
    def aind_burr_6_m_l(self) -> Optional[Decimal]:
        """Maps burr_6_m_l to aind model"""
        return self._map_float_to_decimal(self._nsb.burr_6_m_l)

    @property
    def aind_burr_hole_1(self) -> Optional[BurrHoleProcedure]:
        """Maps burr_hole_1 to aind model"""
        return (
            None
            if self._nsb.burr_hole_1 is None
            else {
                self._nsb.burr_hole_1.SELECT: None,
                self._nsb.burr_hole_1.INJECTION: BurrHoleProcedure.INJECTION,
                self._nsb.burr_hole_1.FIBER_IMPLANT: (
                    BurrHoleProcedure.FIBER_IMPLANT
                ),
                self._nsb.burr_hole_1.INJECTION_FIBER_IMPLANT: (
                    BurrHoleProcedure.INJECTION_FIBER_IMPLANT
                ),
            }.get(self._nsb.burr_hole_1, None)
        )

    @property
    def aind_burr_hole_1_st(self) -> Optional[Any]:
        """Maps burr_hole_1_st to aind model"""
        return (
            None
            if self._nsb.burr_hole_1_st is None
            else {
                self._nsb.burr_hole_1_st.COMPLETE: None,
            }.get(self._nsb.burr_hole_1_st, None)
        )

    @property
    def aind_burr_hole_2(self) -> Optional[BurrHoleProcedure]:
        """Maps burr_hole_2 to aind model"""
        return (
            None
            if self._nsb.burr_hole_2 is None
            else {
                self._nsb.burr_hole_2.SELECT: None,
                self._nsb.burr_hole_2.INJECTION: BurrHoleProcedure.INJECTION,
                self._nsb.burr_hole_2.FIBER_IMPLANT: (
                    BurrHoleProcedure.FIBER_IMPLANT
                ),
                self._nsb.burr_hole_2.INJECTION_FIBER_IMPLANT: (
                    BurrHoleProcedure.INJECTION_FIBER_IMPLANT
                ),
            }.get(self._nsb.burr_hole_2, None)
        )

    @property
    def aind_burr_hole_3(self) -> Optional[BurrHoleProcedure]:
        """Maps burr_hole_3 to aind model"""
        return (
            None
            if self._nsb.burr_hole_3 is None
            else {
                self._nsb.burr_hole_3.SELECT: None,
                self._nsb.burr_hole_3.INJECTION: BurrHoleProcedure.INJECTION,
                self._nsb.burr_hole_3.FIBER_IMPLANT: (
                    BurrHoleProcedure.FIBER_IMPLANT
                ),
                self._nsb.burr_hole_3.INJECTION_FIBER_IMPLANT: (
                    BurrHoleProcedure.INJECTION_FIBER_IMPLANT
                ),
            }.get(self._nsb.burr_hole_3, None)
        )

    @property
    def aind_burr_hole_4(self) -> Optional[BurrHoleProcedure]:
        """Maps burr_hole_4 to aind model"""
        return (
            None
            if self._nsb.burr_hole_4 is None
            else {
                self._nsb.burr_hole_4.SELECT: None,
                self._nsb.burr_hole_4.INJECTION: BurrHoleProcedure.INJECTION,
                self._nsb.burr_hole_4.FIBER_IMPLANT: (
                    BurrHoleProcedure.FIBER_IMPLANT
                ),
                self._nsb.burr_hole_4.INJECTION_FIBER_IMPLANT: (
                    BurrHoleProcedure.INJECTION_FIBER_IMPLANT
                ),
            }.get(self._nsb.burr_hole_4, None)
        )

    @property
    def aind_burr_hole_5(self) -> Optional[BurrHoleProcedure]:
        """Maps burr_hole_5 to aind model"""
        return (
            None
            if self._nsb.burr_hole_5 is None
            else {
                self._nsb.burr_hole_5.SELECT: None,
                self._nsb.burr_hole_5.INJECTION: BurrHoleProcedure.INJECTION,
                self._nsb.burr_hole_5.FIBER_IMPLANT: (
                    BurrHoleProcedure.FIBER_IMPLANT
                ),
                self._nsb.burr_hole_5.INJECTION_FIBER_IMPLANT: (
                    BurrHoleProcedure.INJECTION_FIBER_IMPLANT
                ),
            }.get(self._nsb.burr_hole_5, None)
        )

    @property
    def aind_burr_hole_6(self) -> Optional[BurrHoleProcedure]:
        """Maps burr_hole_6 to aind model"""
        return (
            None
            if self._nsb.burr_hole_6 is None
            else {
                self._nsb.burr_hole_6.SELECT: None,
                self._nsb.burr_hole_6.INJECTION: BurrHoleProcedure.INJECTION,
                self._nsb.burr_hole_6.FIBER_IMPLANT: (
                    BurrHoleProcedure.FIBER_IMPLANT
                ),
                self._nsb.burr_hole_6.INJECTION_FIBER_IMPLANT: (
                    BurrHoleProcedure.INJECTION_FIBER_IMPLANT
                ),
            }.get(self._nsb.burr_hole_6, None)
        )

    @property
    def aind_color_tag(self) -> Optional[str]:
        """Maps color_tag to aind model"""
        return self._nsb.color_tag

    @property
    def aind_com_coplanar(self) -> Optional[Any]:
        """Maps com_coplanar to aind model"""
        return (
            None
            if self._nsb.com_coplanar is None
            else {
                self._nsb.com_coplanar.SELECT: None,
                self._nsb.com_coplanar.NONE: None,
                self._nsb.com_coplanar.MILD: None,
                self._nsb.com_coplanar.MODERATE: None,
                self._nsb.com_coplanar.SEVERE: None,
                self._nsb.com_coplanar.NA: None,
            }.get(self._nsb.com_coplanar, None)
        )

    @property
    def aind_com_damage(self) -> Optional[Any]:
        """Maps com_damage to aind model"""
        return (
            None
            if self._nsb.com_damage is None
            else {
                self._nsb.com_damage.SELECT: None,
                self._nsb.com_damage.NONE: None,
                self._nsb.com_damage.MILD: None,
                self._nsb.com_damage.MODERATE: None,
                self._nsb.com_damage.SEVERE: None,
                self._nsb.com_damage.NA: None,
            }.get(self._nsb.com_damage, None)
        )

    @property
    def aind_com_durotomy(self) -> Optional[Any]:
        """Maps com_durotomy to aind model"""
        return (
            None
            if self._nsb.com_durotomy is None
            else {
                self._nsb.com_durotomy.SELECT: None,
                self._nsb.com_durotomy.COMPLETE: None,
                self._nsb.com_durotomy.TORN_COMPLETE: None,
                self._nsb.com_durotomy.PARTIAL: None,
                self._nsb.com_durotomy.NO: None,
                self._nsb.com_durotomy.UNINTENTIONAL: None,
                self._nsb.com_durotomy.NA: None,
            }.get(self._nsb.com_durotomy, None)
        )

    @property
    def aind_com_sinusbleed(self) -> Optional[Any]:
        """Maps com_sinusbleed to aind model"""
        return (
            None
            if self._nsb.com_sinusbleed is None
            else {
                self._nsb.com_sinusbleed.SELECT: None,
                self._nsb.com_sinusbleed.NONE: None,
                self._nsb.com_sinusbleed.MILD: None,
                self._nsb.com_sinusbleed.MODERATE: None,
                self._nsb.com_sinusbleed.SEVERE: None,
                self._nsb.com_sinusbleed.NA: None,
            }.get(self._nsb.com_sinusbleed, None)
        )

    @property
    def aind_com_swelling(self) -> Optional[Any]:
        """Maps com_swelling to aind model"""
        return (
            None
            if self._nsb.com_swelling is None
            else {
                self._nsb.com_swelling.SELECT: None,
                self._nsb.com_swelling.NONE: None,
                self._nsb.com_swelling.MILD: None,
                self._nsb.com_swelling.MODERATE: None,
                self._nsb.com_swelling.SEVERE: None,
                self._nsb.com_swelling.NA: None,
            }.get(self._nsb.com_swelling, None)
        )

    @property
    def aind_com_window(self) -> Optional[Any]:
        """Maps com_window to aind model"""
        return (
            None
            if self._nsb.com_window is None
            else {
                self._nsb.com_window.SELECT: None,
                self._nsb.com_window.CENTRAL: None,
                self._nsb.com_window.ANTERIOR: None,
                self._nsb.com_window.LATERAL: None,
                self._nsb.com_window.MEDIAL: None,
                self._nsb.com_window.POSTERIOR: None,
                self._nsb.com_window.OTHER_IN_COMMENTS: None,
                self._nsb.com_window.NA: None,
            }.get(self._nsb.com_window, None)
        )

    @property
    def aind_compliance_asset_id(self) -> Optional[str]:
        """Maps compliance_asset_id to aind model"""
        return self._nsb.compliance_asset_id

    @property
    def aind_contusion(self) -> Optional[Any]:
        """Maps contusion to aind model"""
        return (
            None
            if self._nsb.contusion is None
            else {
                self._nsb.contusion.SELECT: None,
                self._nsb.contusion.NONE: None,
                self._nsb.contusion.MILD: None,
                self._nsb.contusion.MODERATE: None,
                self._nsb.contusion.SEVERE: None,
                self._nsb.contusion.NA: None,
            }.get(self._nsb.contusion, None)
        )

    @property
    def aind_craniotomy_perform_d(self) -> Optional[During]:
        """Maps craniotomy_perform_d to aind model"""
        return (
            None
            if self._nsb.craniotomy_perform_d is None
            else {
                self._nsb.craniotomy_perform_d.INITIAL_SURGERY: During.INITIAL,
                self._nsb.craniotomy_perform_d.FOLLOW_UP_SURGERY: During.FOLLOW_UP,
            }.get(self._nsb.craniotomy_perform_d, None)
        )

    @property
    def aind_craniotomy_type(self) -> Optional[CraniotomyType]:
        """Maps craniotomy_type to aind model"""
        return (
            None
            if self._nsb.craniotomy_type is None
            else {
                self._nsb.craniotomy_type.SELECT: None,
                self._nsb.craniotomy_type.N_3MM: CraniotomyType.THREE_MM,
                self._nsb.craniotomy_type.N_5MM: CraniotomyType.FIVE_MM,
                self._nsb.craniotomy_type.WHC_2_P: CraniotomyType.WHC,
                self._nsb.craniotomy_type.WHC_NP: CraniotomyType.WHC,
            }.get(self._nsb.craniotomy_type, None)
        )

    @property
    def aind_created(self) -> Optional[datetime]:
        """Maps created to aind model"""
        return self._nsb.created

    @property
    def aind_date1st_injection(self) -> Optional[date]:
        """Maps date1st_injection to aind model"""
        return self._parse_datetime_to_date(self._nsb.date1st_injection)

    @property
    def aind_date_of_birth(self) -> Optional[datetime]:
        """Maps date_of_birth to aind model"""
        return self._nsb.date_of_birth

    @property
    def aind_date_of_surgery(self) -> Optional[date]:
        """Maps date_of_surgery to aind model"""
        return self._parse_datetime_to_date(self._nsb.date_of_surgery)

    @property
    def aind_date_range_start(self) -> Optional[datetime]:
        """Maps date_range_start to aind model"""
        return self._nsb.date_range_start

    @property
    def aind_dv2nd_inj(self) -> Optional[Decimal]:
        """Maps dv2nd_inj to aind model"""
        return self._map_float_to_decimal(self._nsb.dv2nd_inj)

    @property
    def aind_editor_id(self) -> Optional[int]:
        """Maps editor_id to aind model"""
        return self._nsb.editor_id

    @property
    def aind_fiber_implant1_dv(self) -> Optional[Decimal]:
        """Maps fiber_implant1_dv to aind model"""
        return self._map_float_to_decimal(self._nsb.fiber_implant1_dv)

    @property
    def aind_fiber_implant1_lengt(self) -> Optional[Decimal]:
        """Maps fiber_implant1_lengt to aind model"""
        return self._parse_fiber_length_mm_str(self._nsb.fiber_implant1_lengt)

    @property
    def aind_fiber_implant2_dv(self) -> Optional[Decimal]:
        """Maps fiber_implant2_dv to aind model"""
        return self._map_float_to_decimal(self._nsb.fiber_implant2_dv)

    @property
    def aind_fiber_implant2_lengt(self) -> Optional[Decimal]:
        """Maps fiber_implant2_lengt to aind model"""
        return self._parse_fiber_length_mm_str(self._nsb.fiber_implant2_lengt)

    @property
    def aind_fiber_implant3_d_x00(self) -> Optional[Decimal]:
        """Maps fiber_implant3_d_x00 to aind model"""
        return self._map_float_to_decimal(self._nsb.fiber_implant3_d_x00)

    @property
    def aind_fiber_implant3_lengt(self) -> Optional[Decimal]:
        """Maps fiber_implant3_lengt to aind model"""
        return self._parse_fiber_length_mm_str(self._nsb.fiber_implant3_lengt)

    @property
    def aind_fiber_implant4_d_x00(self) -> Optional[Decimal]:
        """Maps fiber_implant4_d_x00 to aind model"""
        return self._map_float_to_decimal(self._nsb.fiber_implant4_d_x00)

    @property
    def aind_fiber_implant4_lengt(self) -> Optional[Decimal]:
        """Maps fiber_implant4_lengt to aind model"""
        return self._parse_fiber_length_mm_str(self._nsb.fiber_implant4_lengt)

    @property
    def aind_fiber_implant5_d_x00(self) -> Optional[Decimal]:
        """Maps fiber_implant5_d_x00 to aind model"""
        return self._map_float_to_decimal(self._nsb.fiber_implant5_d_x00)

    @property
    def aind_fiber_implant5_lengt(self) -> Optional[Decimal]:
        """Maps fiber_implant5_lengt to aind model"""
        return self._parse_fiber_length_mm_str(self._nsb.fiber_implant5_lengt)

    @property
    def aind_fiber_implant6_d_x00(self) -> Optional[Decimal]:
        """Maps fiber_implant6_d_x00 to aind model"""
        return self._map_float_to_decimal(self._nsb.fiber_implant6_d_x00)

    @property
    def aind_fiber_implant6_lengt(self) -> Optional[Decimal]:
        """Maps fiber_implant6_lengt to aind model"""
        return self._parse_fiber_length_mm_str(self._nsb.fiber_implant6_lengt)

    @property
    def aind_first_inj_recovery(self) -> Optional[Decimal]:
        """Maps first_inj_recovery to aind model"""
        return self._map_float_to_decimal(self._nsb.first_inj_recovery)

    @property
    def aind_first_injection_iso_durat(self) -> Optional[Decimal]:
        """Maps first_injection_iso_durat to aind model"""
        optional_decimal = self._map_float_to_decimal(
            self._nsb.first_injection_iso_durat
        )
        return None if optional_decimal is None else optional_decimal * 60

    @property
    def aind_first_injection_weight_af(self) -> Optional[Decimal]:
        """Maps first_injection_weight_af to aind model"""
        return self._map_float_to_decimal(self._nsb.first_injection_weight_af)

    @property
    def aind_first_injection_weight_be(self) -> Optional[Decimal]:
        """Maps first_injection_weight_be to aind model"""
        return self._map_float_to_decimal(self._nsb.first_injection_weight_be)

    @property
    def aind_headpost(self) -> Optional[HeadPost]:
        """Maps headpost to aind model"""
        return (
            None
            if self._nsb.headpost is None
            else {
                self._nsb.headpost.SELECT: None,
                self._nsb.headpost.VISUAL_CTX: HeadPost.VISUAL_CTX,
                self._nsb.headpost.FRONTAL_CTX: HeadPost.FRONTAL_CTX,
                self._nsb.headpost.MOTOR_CTX: HeadPost.MOTOR_CTX,
                self._nsb.headpost.WHC_FULL_RING: HeadPost.WHC_FULL_RING,
                self._nsb.headpost.LSHAPED: HeadPost.L_SHAPED,
                self._nsb.headpost.WHC_NP_ZIRCONIA: HeadPost.WHC_NP_ZIRCONIA,
                self._nsb.headpost.AI_STRAIGHT_BAR: HeadPost.AI_HEADBAR,
                self._nsb.headpost.LC: HeadPost.LC,
                self._nsb.headpost.WHC_NP: HeadPost.WHC_NP,
                self._nsb.headpost.WHC_2P: HeadPost.WHC_2P,
                self._nsb.headpost.OTHER_ADD_DETAILS_IN_REQU: None,
            }.get(self._nsb.headpost, None)
        )

    @property
    def aind_headpost_perform_dur(self) -> Optional[During]:
        """Maps headpost_perform_dur to aind model"""
        return (
            None
            if self._nsb.headpost_perform_dur is None
            else {
                self._nsb.headpost_perform_dur.INITIAL_SURGERY: During.INITIAL,
                self._nsb.headpost_perform_dur.FOLLOW_UP_SURGERY: During.FOLLOW_UP,
            }.get(self._nsb.headpost_perform_dur, None)
        )

    @property
    def aind_headpost_type(self) -> Optional[HeadPostType]:
        """Maps headpost_type to aind model"""
        # TODO: check HeadpostTypes WHC NP Zirconia and AI Straight Bar Well
        return (
            None
            if self._nsb.headpost_type is None
            else {
                self._nsb.headpost_type.SELECT: None,
                self._nsb.headpost_type.NO_WELL: HeadPostType.NO_WELL,
                self._nsb.headpost_type.SCIENTIFICA_CAM: HeadPostType.CAM,
                self._nsb.headpost_type.MESOSCOPE: HeadPostType.MESOSCOPE,
                self._nsb.headpost_type.NEUROPIXEL: HeadPostType.NEUROPIXEL,
                self._nsb.headpost_type.WHC_2_P: HeadPostType.WHC_2P,
                self._nsb.headpost_type.WHC_NP: HeadPostType.WHC_NP,
                self._nsb.headpost_type.WHC_NP_ZIRCONIA: HeadPostType.WHC_NP_ZIRCONIA,
                self._nsb.headpost_type.AI_STRAIGHT_BAR_WELL: HeadPostType.AI_STRAIGHT_BAR_WELL,
                self._nsb.headpost_type.OTHER_SEE_REQUESTOR_COMME: None,
            }.get(self._nsb.headpost_type, None)
        )

    @property
    def aind_hemisphere2nd_inj(self) -> Optional[Side]:
        """Maps hemisphere2nd_inj to aind model"""
        return (
            None
            if self._nsb.hemisphere2nd_inj is None
            else {
                self._nsb.hemisphere2nd_inj.SELECT: None,
                self._nsb.hemisphere2nd_inj.LEFT: Side.LEFT,
                self._nsb.hemisphere2nd_inj.RIGHT: Side.RIGHT,
            }.get(self._nsb.hemisphere2nd_inj, None)
        )

    @property
    def aind_hp_iso_level(self) -> Optional[Decimal]:
        """Maps hp_iso_level to aind model"""
        return self._map_float_to_decimal(self._nsb.hp_iso_level)

    @property
    def aind_hp_recovery(self) -> Optional[Decimal]:
        """Maps hp_recovery to aind model"""
        return self._map_float_to_decimal(self._nsb.hp_recovery)

    @property
    def aind_hp_surgeon_comments(self) -> Optional[str]:
        """Maps hp_surgeon_comments to aind model"""
        return self._nsb.hp_surgeon_comments

    @property
    def aind_hp_work_station(self) -> Optional[str]:
        """Maps hp_work_station to aind model"""
        return (
            None
            if self._nsb.hp_work_station is None
            else {
                self._nsb.hp_work_station.SELECT: None,
                self._nsb.hp_work_station.SWS_1: (
                    self._nsb.hp_work_station.SWS_1.value
                ),
                self._nsb.hp_work_station.SWS_2: (
                    self._nsb.hp_work_station.SWS_2.value
                ),
                self._nsb.hp_work_station.SWS_3: (
                    self._nsb.hp_work_station.SWS_3.value
                ),
                self._nsb.hp_work_station.SWS_4: (
                    self._nsb.hp_work_station.SWS_4.value
                ),
                self._nsb.hp_work_station.SWS_5: (
                    self._nsb.hp_work_station.SWS_5.value
                ),
                self._nsb.hp_work_station.SWS_6: (
                    self._nsb.hp_work_station.SWS_6.value
                ),
                self._nsb.hp_work_station.SWS_7: (
                    self._nsb.hp_work_station.SWS_7.value
                ),
                self._nsb.hp_work_station.SWS_8: (
                    self._nsb.hp_work_station.SWS_8.value
                ),
                self._nsb.hp_work_station.SWS_9: (
                    self._nsb.hp_work_station.SWS_9.value
                ),
            }.get(self._nsb.hp_work_station, None)
        )

    @property
    def aind_iacuc_protocol(self) -> Optional[str]:
        """Maps iacuc_protocol to aind model"""
        return (
            None
            if self._nsb.iacuc_protocol is None
            else {
                self._nsb.iacuc_protocol.SELECT: None,
                self._nsb.iacuc_protocol.N_1906: (
                    self._nsb.iacuc_protocol.N_1906.value
                ),
                self._nsb.iacuc_protocol.N_2001: (
                    self._nsb.iacuc_protocol.N_2001.value
                ),
                self._nsb.iacuc_protocol.N_2003: (
                    self._nsb.iacuc_protocol.N_2003.value
                ),
                self._nsb.iacuc_protocol.N_2004: (
                    self._nsb.iacuc_protocol.N_2004.value
                ),
                self._nsb.iacuc_protocol.N_2005: (
                    self._nsb.iacuc_protocol.N_2005.value
                ),
                self._nsb.iacuc_protocol.N_2006: (
                    self._nsb.iacuc_protocol.N_2006.value
                ),
                self._nsb.iacuc_protocol.N_2011: (
                    self._nsb.iacuc_protocol.N_2011.value
                ),
                self._nsb.iacuc_protocol.N_2102: (
                    self._nsb.iacuc_protocol.N_2102.value
                ),
                self._nsb.iacuc_protocol.N_2103: (
                    self._nsb.iacuc_protocol.N_2103.value
                ),
                self._nsb.iacuc_protocol.N_2104: (
                    self._nsb.iacuc_protocol.N_2104.value
                ),
                self._nsb.iacuc_protocol.N_2105: (
                    self._nsb.iacuc_protocol.N_2105.value
                ),
                self._nsb.iacuc_protocol.N_2106: (
                    self._nsb.iacuc_protocol.N_2106.value
                ),
                self._nsb.iacuc_protocol.N_2107: (
                    self._nsb.iacuc_protocol.N_2107.value
                ),
                self._nsb.iacuc_protocol.N_2108: (
                    self._nsb.iacuc_protocol.N_2108.value
                ),
                self._nsb.iacuc_protocol.N_2109: (
                    self._nsb.iacuc_protocol.N_2109.value
                ),
                self._nsb.iacuc_protocol.N_2110: (
                    self._nsb.iacuc_protocol.N_2110.value
                ),
                self._nsb.iacuc_protocol.N_2113: (
                    self._nsb.iacuc_protocol.N_2113.value
                ),
                self._nsb.iacuc_protocol.N_2115: (
                    self._nsb.iacuc_protocol.N_2115.value
                ),
                self._nsb.iacuc_protocol.N_2117: (
                    self._nsb.iacuc_protocol.N_2117.value
                ),
                self._nsb.iacuc_protocol.N_2201: (
                    self._nsb.iacuc_protocol.N_2201.value
                ),
                self._nsb.iacuc_protocol.N_2202: (
                    self._nsb.iacuc_protocol.N_2202.value
                ),
                self._nsb.iacuc_protocol.N_2205: (
                    self._nsb.iacuc_protocol.N_2205.value
                ),
                self._nsb.iacuc_protocol.N_2212: (
                    self._nsb.iacuc_protocol.N_2212.value
                ),
                self._nsb.iacuc_protocol.N_2301: (
                    self._nsb.iacuc_protocol.N_2301.value
                ),
                self._nsb.iacuc_protocol.N_2304: (
                    self._nsb.iacuc_protocol.N_2304.value
                ),
                self._nsb.iacuc_protocol.N_2305: (
                    self._nsb.iacuc_protocol.N_2305.value
                ),
                self._nsb.iacuc_protocol.N_2306: (
                    self._nsb.iacuc_protocol.N_2306.value
                ),
                self._nsb.iacuc_protocol.N_2010: (
                    self._nsb.iacuc_protocol.N_2010.value
                ),
            }.get(self._nsb.iacuc_protocol, None)
        )

    @property
    def aind_id(self) -> Optional[int]:
        """Maps id to aind model"""
        return self._nsb.id

    @property
    def aind_implant_id_coverslip_type(self) -> Optional[Any]:
        """Maps implant_id_coverslip_type to aind model"""
        return (
            None
            if self._nsb.implant_id_coverslip_type is None
            else self._nsb.implant_id_coverslip_type
        )

    @property
    def aind_inj1_alternating_time(self) -> Optional[str]:
        """Maps inj1_alternating_time to aind model"""
        return self._nsb.inj1_alternating_time

    @property
    def aind_inj1_angle_v2(self) -> Optional[Decimal]:
        """Maps inj1_angle_v2 to aind model"""
        return self._map_float_to_decimal(self._nsb.inj1_angle_v2)

    @property
    def aind_inj1_current(self) -> Optional[Decimal]:
        """Maps inj1_current to aind model"""
        return self._parse_current_str(self._nsb.inj1_current)

    @property
    def aind_inj1_ionto_time(self) -> Optional[Decimal]:
        """Maps inj1_ionto_time to aind model"""
        return self._parse_length_of_time_str(self._nsb.inj1_ionto_time)

    @property
    def aind_inj1_storage_location(self) -> Optional[str]:
        """Maps inj1_storage_location to aind model"""
        return self._nsb.inj1_storage_location

    @property
    def aind_inj1_type(self) -> Optional[InjectionType]:
        """Maps inj1_type to aind model"""
        return (
            None
            if self._nsb.inj1_type is None
            else {
                self._nsb.inj1_type.SELECT: None,
                self._nsb.inj1_type.IONTOPHORESIS: InjectionType.IONTOPHORESIS,
                self._nsb.inj1_type.NANOJECT_PRESSURE: InjectionType.NANOJECT,
            }.get(self._nsb.inj1_type, None)
        )

    @property
    def aind_inj1_virus_strain_rt(self) -> Optional[str]:
        """Maps inj1_virus_strain_rt to aind model"""
        return self._parse_virus_strain_str(self._nsb.inj1_virus_strain_rt)

    @property
    def aind_inj1volperdepth(self) -> Optional[Decimal]:
        """Maps inj1volperdepth to aind model"""
        return self._map_float_to_decimal(self._nsb.inj1volperdepth)

    @property
    def aind_inj2_alternating_time(self) -> Optional[str]:
        """Maps inj2_alternating_time to aind model"""
        return self._nsb.inj2_alternating_time

    @property
    def aind_inj2_angle_v2(self) -> Optional[Decimal]:
        """Maps inj2_angle_v2 to aind model"""
        return self._map_float_to_decimal(self._nsb.inj2_angle_v2)

    @property
    def aind_inj2_current(self) -> Optional[Decimal]:
        """Maps inj2_current to aind model"""
        return self._parse_current_str(self._nsb.inj2_current)

    @property
    def aind_inj2_ionto_time(self) -> Optional[float]:
        """Maps inj2_ionto_time to aind model"""
        return self._parse_length_of_time_str(self._nsb.inj2_ionto_time)

    @property
    def aind_inj2_storage_location(self) -> Optional[str]:
        """Maps inj2_storage_location to aind model"""
        return self._nsb.inj2_storage_location

    @property
    def aind_inj2_type(self) -> Optional[InjectionType]:
        """Maps inj2_type to aind model"""
        return (
            None
            if self._nsb.inj2_type is None
            else {
                self._nsb.inj2_type.SELECT: None,
                self._nsb.inj2_type.IONTOPHORESIS: InjectionType.IONTOPHORESIS,
                self._nsb.inj2_type.NANOJECT_PRESSURE: InjectionType.NANOJECT,
            }.get(self._nsb.inj2_type, None)
        )

    @property
    def aind_inj2_virus_strain_rt(self) -> Optional[str]:
        """Maps inj2_virus_strain_rt to aind model"""
        return self._parse_virus_strain_str(self._nsb.inj2_virus_strain_rt)

    @property
    def aind_inj2volperdepth(self) -> Optional[Decimal]:
        """Maps inj2volperdepth to aind model"""
        return self._map_float_to_decimal(self._nsb.inj2volperdepth)

    @property
    def aind_inj3_alternating_time(self) -> Optional[str]:
        """Maps inj3_alternating_time to aind model"""
        return self._nsb.inj3_alternating_time

    @property
    def aind_inj3_current(self) -> Optional[Decimal]:
        """Maps inj3_current to aind model"""
        return self._parse_current_str(self._nsb.inj3_current)

    @property
    def aind_inj3_ionto_time(self) -> Optional[Decimal]:
        """Maps inj3_ionto_time to aind model"""
        return self._parse_length_of_time_str(self._nsb.inj3_ionto_time)

    @property
    def aind_inj3_storage_location(self) -> Optional[str]:
        """Maps inj3_storage_location to aind model"""
        return self._nsb.inj3_storage_location

    @property
    def aind_inj3_type(self) -> Optional[InjectionType]:
        """Maps inj3_type to aind model"""
        return (
            None
            if self._nsb.inj3_type is None
            else {
                self._nsb.inj3_type.SELECT: None,
                self._nsb.inj3_type.IONTOPHORESIS: InjectionType.IONTOPHORESIS,
                self._nsb.inj3_type.NANOJECT_PRESSURE: InjectionType.NANOJECT,
            }.get(self._nsb.inj3_type, None)
        )

    @property
    def aind_inj3ret_setting(self) -> Optional[Any]:
        """Maps inj3ret_setting to aind model"""
        return (
            None
            if self._nsb.inj3ret_setting is None
            else {
                self._nsb.inj3ret_setting.OFF: None,
                self._nsb.inj3ret_setting.ON: None,
            }.get(self._nsb.inj3ret_setting, None)
        )

    @property
    def aind_inj3volperdepth(self) -> Optional[Decimal]:
        """Maps inj3volperdepth to aind model"""
        return self._map_float_to_decimal(self._nsb.inj3volperdepth)

    @property
    def aind_inj4_alternating_time(self) -> Optional[str]:
        """Maps inj4_alternating_time to aind model"""
        return self._nsb.inj4_alternating_time

    @property
    def aind_inj4_current(self) -> Optional[Decimal]:
        """Maps inj4_current to aind model"""
        return self._parse_current_str(self._nsb.inj4_current)

    @property
    def aind_inj4_ionto_time(self) -> Optional[Decimal]:
        """Maps inj4_ionto_time to aind model"""
        return self._parse_length_of_time_str(self._nsb.inj4_ionto_time)

    @property
    def aind_inj4_storage_location(self) -> Optional[str]:
        """Maps inj4_storage_location to aind model"""
        return self._nsb.inj4_storage_location

    @property
    def aind_inj4_type(self) -> Optional[InjectionType]:
        """Maps inj4_type to aind model"""
        return (
            None
            if self._nsb.inj4_type is None
            else {
                self._nsb.inj4_type.SELECT: None,
                self._nsb.inj4_type.IONTOPHORESIS: InjectionType.IONTOPHORESIS,
                self._nsb.inj4_type.NANOJECT_PRESSURE: InjectionType.NANOJECT,
            }.get(self._nsb.inj4_type, None)
        )

    @property
    def aind_inj4_virus_strain_rt(self) -> Optional[str]:
        """Maps inj4_virus_strain_rt to aind model"""
        return self._parse_virus_strain_str(self._nsb.inj4_virus_strain_rt)

    @property
    def aind_inj4ret_setting(self) -> Optional[Any]:
        """Maps inj4ret_setting to aind model"""
        return (
            None
            if self._nsb.inj4ret_setting is None
            else {
                self._nsb.inj4ret_setting.OFF: None,
                self._nsb.inj4ret_setting.ON: None,
            }.get(self._nsb.inj4ret_setting, None)
        )

    @property
    def aind_inj4volperdepth(self) -> Optional[Decimal]:
        """Maps inj4volperdepth to aind model"""
        return self._map_float_to_decimal(self._nsb.inj4volperdepth)

    @property
    def aind_inj5_alternating_time(self) -> Optional[str]:
        """Maps inj5_alternating_time to aind model"""
        return self._nsb.inj5_alternating_time

    @property
    def aind_inj5_current(self) -> Optional[Decimal]:
        """Maps inj5_current to aind model"""
        return self._parse_current_str(self._nsb.inj5_current)

    @property
    def aind_inj5_ionto_time(self) -> Optional[Decimal]:
        """Maps inj5_ionto_time to aind model"""
        return self._parse_length_of_time_str(self._nsb.inj5_ionto_time)

    @property
    def aind_inj5_storage_location(self) -> Optional[str]:
        """Maps inj5_storage_location to aind model"""
        return self._nsb.inj5_storage_location

    @property
    def aind_inj5_type(self) -> Optional[InjectionType]:
        """Maps inj5_type to aind model"""
        return (
            None
            if self._nsb.inj5_type is None
            else {
                self._nsb.inj5_type.SELECT: None,
                self._nsb.inj5_type.IONTOPHORESIS: InjectionType.IONTOPHORESIS,
                self._nsb.inj5_type.NANOJECT_PRESSURE: InjectionType.NANOJECT,
            }.get(self._nsb.inj5_type, None)
        )

    @property
    def aind_inj5_virus_strain_rt(self) -> Optional[str]:
        """Maps inj5_virus_strain_rt to aind model"""
        return self._parse_virus_strain_str(self._nsb.inj5_virus_strain_rt)

    @property
    def aind_inj5ret_setting(self) -> Optional[Any]:
        """Maps inj5ret_setting to aind model"""
        return (
            None
            if self._nsb.inj5ret_setting is None
            else {
                self._nsb.inj5ret_setting.OFF: None,
                self._nsb.inj5ret_setting.ON: None,
            }.get(self._nsb.inj5ret_setting, None)
        )

    @property
    def aind_inj5volperdepth(self) -> Optional[Decimal]:
        """Maps inj5volperdepth to aind model"""
        return self._map_float_to_decimal(self._nsb.inj5volperdepth)

    @property
    def aind_inj6_alternating_time(self) -> Optional[str]:
        """Maps inj6_alternating_time to aind model"""
        return self._nsb.inj6_alternating_time

    @property
    def aind_inj6_current(self) -> Optional[Decimal]:
        """Maps inj6_current to aind model"""
        return self._parse_current_str(self._nsb.inj6_current)

    @property
    def aind_inj6_ionto_time(self) -> Optional[Decimal]:
        """Maps inj6_ionto_time to aind model"""
        return self._parse_length_of_time_str(self._nsb.inj6_ionto_time)

    @property
    def aind_inj6_storage_location(self) -> Optional[str]:
        """Maps inj6_storage_location to aind model"""
        return self._nsb.inj6_storage_location

    @property
    def aind_inj6_type(self) -> Optional[InjectionType]:
        """Maps inj6_type to aind model"""
        return (
            None
            if self._nsb.inj6_type is None
            else {
                self._nsb.inj6_type.SELECT: None,
                self._nsb.inj6_type.IONTOPHORESIS: InjectionType.IONTOPHORESIS,
                self._nsb.inj6_type.NANOJECT_PRESSURE: InjectionType.NANOJECT,
            }.get(self._nsb.inj6_type, None)
        )

    @property
    def aind_inj6_virus_strain_rt(self) -> Optional[str]:
        """Maps inj6_virus_strain_rt to aind model"""
        return self._parse_virus_strain_str(self._nsb.inj6_virus_strain_rt)

    @property
    def aind_inj6ret_setting(self) -> Optional[Any]:
        """Maps inj6ret_setting to aind model"""
        return (
            None
            if self._nsb.inj6ret_setting is None
            else {
                self._nsb.inj6ret_setting.OFF: None,
                self._nsb.inj6ret_setting.ON: None,
            }.get(self._nsb.inj6ret_setting, None)
        )

    @property
    def aind_inj6volperdepth(self) -> Optional[Decimal]:
        """Maps inj6volperdepth to aind model"""
        return self._map_float_to_decimal(self._nsb.inj6volperdepth)

    @property
    def aind_inj_virus_strain_rt(self) -> Optional[str]:
        """Maps inj_virus_strain_rt to aind model"""
        return self._parse_virus_strain_str(self._nsb.inj_virus_strain_rt)

    @property
    def aind_ionto_number_inj1(self) -> Optional[str]:
        """Maps ionto_number_inj1 to aind model"""
        return (
            None
            if self._nsb.ionto_number_inj1 is None
            else {
                self._nsb.ionto_number_inj1.SELECT: None,
                self._nsb.ionto_number_inj1.IONTO_1: (
                    self._nsb.ionto_number_inj1.IONTO_1.value
                ),
                self._nsb.ionto_number_inj1.IONTO_2: (
                    self._nsb.ionto_number_inj1.IONTO_2.value
                ),
                self._nsb.ionto_number_inj1.IONTO_3: (
                    self._nsb.ionto_number_inj1.IONTO_3.value
                ),
                self._nsb.ionto_number_inj1.IONTO_4: (
                    self._nsb.ionto_number_inj1.IONTO_4.value
                ),
                self._nsb.ionto_number_inj1.IONTO_5: (
                    self._nsb.ionto_number_inj1.IONTO_5.value
                ),
                self._nsb.ionto_number_inj1.IONTO_6: (
                    self._nsb.ionto_number_inj1.IONTO_6.value
                ),
                self._nsb.ionto_number_inj1.IONTO_7: (
                    self._nsb.ionto_number_inj1.IONTO_7.value
                ),
                self._nsb.ionto_number_inj1.IONTO_8: (
                    self._nsb.ionto_number_inj1.IONTO_8.value
                ),
                self._nsb.ionto_number_inj1.IONTO_9: (
                    self._nsb.ionto_number_inj1.IONTO_9.value
                ),
                self._nsb.ionto_number_inj1.IONTO_10: (
                    self._nsb.ionto_number_inj1.IONTO_10.value
                ),
                self._nsb.ionto_number_inj1.NA: None,
            }.get(self._nsb.ionto_number_inj1, None)
        )

    @property
    def aind_ionto_number_inj2(self) -> Optional[str]:
        """Maps ionto_number_inj2 to aind model"""
        return (
            None
            if self._nsb.ionto_number_inj2 is None
            else {
                self._nsb.ionto_number_inj2.SELECT: None,
                self._nsb.ionto_number_inj2.IONTO_1: (
                    self._nsb.ionto_number_inj2.IONTO_1.value
                ),
                self._nsb.ionto_number_inj2.IONTO_2: (
                    self._nsb.ionto_number_inj2.IONTO_2.value
                ),
                self._nsb.ionto_number_inj2.IONTO_3: (
                    self._nsb.ionto_number_inj2.IONTO_3.value
                ),
                self._nsb.ionto_number_inj2.IONTO_4: (
                    self._nsb.ionto_number_inj2.IONTO_4.value
                ),
                self._nsb.ionto_number_inj2.IONTO_5: (
                    self._nsb.ionto_number_inj2.IONTO_5.value
                ),
                self._nsb.ionto_number_inj2.IONTO_6: (
                    self._nsb.ionto_number_inj2.IONTO_6.value
                ),
                self._nsb.ionto_number_inj2.IONTO_7: (
                    self._nsb.ionto_number_inj2.IONTO_7.value
                ),
                self._nsb.ionto_number_inj2.IONTO_8: (
                    self._nsb.ionto_number_inj2.IONTO_8.value
                ),
                self._nsb.ionto_number_inj2.IONTO_9: (
                    self._nsb.ionto_number_inj2.IONTO_9.value
                ),
                self._nsb.ionto_number_inj2.IONTO_10: (
                    self._nsb.ionto_number_inj2.IONTO_10.value
                ),
                self._nsb.ionto_number_inj2.NA: None,
            }.get(self._nsb.ionto_number_inj2, None)
        )

    @property
    def aind_iso_on(self) -> Optional[Decimal]:
        """Maps iso_on to aind model"""
        optional_decimal = self._map_float_to_decimal(self._nsb.iso_on)
        return None if optional_decimal is None else optional_decimal * 60

    @property
    def aind_lab_tracks_group(self) -> Optional[str]:
        """Maps lab_tracks_group to aind model"""
        return self._nsb.lab_tracks_group

    @property
    def aind_lab_tracks_id1(self) -> Optional[str]:
        """Maps lab_tracks_id1 to aind model"""
        return self._nsb.lab_tracks_id1

    @property
    def aind_lab_tracks_requestor(self) -> Optional[str]:
        """Maps lab_tracks_requestor to aind model"""
        return self._nsb.lab_tracks_requestor

    @property
    def aind_li_ms_required(self) -> Optional[Any]:
        """Maps li_ms_required to aind model"""
        return (
            None
            if self._nsb.li_ms_required is None
            else {
                self._nsb.li_ms_required.SELECT: None,
                self._nsb.li_ms_required.YES: None,
                self._nsb.li_ms_required.NO: None,
            }.get(self._nsb.li_ms_required, None)
        )

    @property
    def aind_light_cycle(self) -> Optional[Any]:
        """Maps light_cycle to aind model"""
        return (
            None
            if self._nsb.light_cycle is None
            else {
                self._nsb.light_cycle.STANDARD_LIGHT_CYCLE_6AM: None,
                self._nsb.light_cycle.REVERSE_LIGHT_CYCLE_9PM_T: None,
            }.get(self._nsb.light_cycle, None)
        )

    @property
    def aind_lims_project(self) -> Optional[Any]:
        """Maps lims_project to aind model"""
        return (
            None
            if self._nsb.lims_project is None
            else {
                self._nsb.lims_project.N_0200: None,
                self._nsb.lims_project.N_0309: None,
                self._nsb.lims_project.N_0310: None,
                self._nsb.lims_project.N_0311: None,
                self._nsb.lims_project.N_0312: None,
                self._nsb.lims_project.N_0314: None,
                self._nsb.lims_project.N_0316: None,
                self._nsb.lims_project.N_0319: None,
                self._nsb.lims_project.N_0320: None,
                self._nsb.lims_project.N_0321: None,
                self._nsb.lims_project.N_03212: None,
                self._nsb.lims_project.N_03213: None,
                self._nsb.lims_project.N_03214: None,
                self._nsb.lims_project.N_0322: None,
                self._nsb.lims_project.N_0324: None,
                self._nsb.lims_project.N_0325: None,
                self._nsb.lims_project.N_0326: None,
                self._nsb.lims_project.N_0327: None,
                self._nsb.lims_project.N_03272: None,
                self._nsb.lims_project.N_0328: None,
                self._nsb.lims_project.N_0329: None,
                self._nsb.lims_project.N_0331: None,
                self._nsb.lims_project.N_0334: None,
                self._nsb.lims_project.N_03342: None,
                self._nsb.lims_project.N_0335: None,
                self._nsb.lims_project.N_0336: None,
                self._nsb.lims_project.N_0338: None,
                self._nsb.lims_project.N_0339: None,
                self._nsb.lims_project.N_03392: None,
                self._nsb.lims_project.N_0340: None,
                self._nsb.lims_project.N_0342: None,
                self._nsb.lims_project.N_03422: None,
                self._nsb.lims_project.N_0343: None,
                self._nsb.lims_project.N_0344: None,
                self._nsb.lims_project.N_0345: None,
                self._nsb.lims_project.N_0346: None,
                self._nsb.lims_project.N_0350: None,
                self._nsb.lims_project.N_0350X: None,
                self._nsb.lims_project.N_0351: None,
                self._nsb.lims_project.N_0351X: None,
                self._nsb.lims_project.N_0354: None,
                self._nsb.lims_project.N_0355: None,
                self._nsb.lims_project.N_0357: None,
                self._nsb.lims_project.N_0358: None,
                self._nsb.lims_project.N_0359: None,
                self._nsb.lims_project.N_0360: None,
                self._nsb.lims_project.N_03602: None,
                self._nsb.lims_project.N_0362: None,
                self._nsb.lims_project.N_0363: None,
                self._nsb.lims_project.N_0364: None,
                self._nsb.lims_project.N_0365: None,
                self._nsb.lims_project.N_0365X: None,
                self._nsb.lims_project.N_0366: None,
                self._nsb.lims_project.N_0366X: None,
                self._nsb.lims_project.N_0367: None,
                self._nsb.lims_project.N_0369: None,
                self._nsb.lims_project.N_0371: None,
                self._nsb.lims_project.N_0372: None,
                self._nsb.lims_project.N_0372X: None,
                self._nsb.lims_project.N_0374: None,
                self._nsb.lims_project.N_0376: None,
                self._nsb.lims_project.N_0376A: None,
                self._nsb.lims_project.N_0376X: None,
                self._nsb.lims_project.N_0378: None,
                self._nsb.lims_project.N_0378X: None,
                self._nsb.lims_project.N_0380: None,
                self._nsb.lims_project.N_0384: None,
                self._nsb.lims_project.N_0386: None,
                self._nsb.lims_project.N_0388: None,
                self._nsb.lims_project.AINDMSMA: None,
                self._nsb.lims_project.AINDDISCOVERY: None,
                self._nsb.lims_project.AINDEPHYS: None,
                self._nsb.lims_project.AINDOPHYS: None,
                self._nsb.lims_project.APR_OX: None,
                self._nsb.lims_project.A_XL_OX: None,
                self._nsb.lims_project.BA_RSEQ_GENETIC_TOOLS: None,
                self._nsb.lims_project.BRAIN_STIM: None,
                self._nsb.lims_project.BRAINTV_VIRAL_STRATEGIES: None,
                self._nsb.lims_project.C200: None,
                self._nsb.lims_project.C600: None,
                self._nsb.lims_project.C600_LATERAL: None,
                self._nsb.lims_project.C600X: None,
                self._nsb.lims_project.CELLTYPES_TRANSGENIC_CHAR: None,
                self._nsb.lims_project.CITRICACIDPILOT: None,
                self._nsb.lims_project.CON9999: None,
                self._nsb.lims_project.CONC505: None,
                self._nsb.lims_project.CONCS04: None,
                self._nsb.lims_project.DEEPSCOPE_SLM_DEVELOPMENT: None,
                self._nsb.lims_project.DYNAMIC_ROUTING_BEHAVIOR: None,
                self._nsb.lims_project.DYNAMIC_ROUTING_OPTO_DEV: None,
                self._nsb.lims_project.DYNAMIC_ROUTING_SURGICAL: None,
                self._nsb.lims_project.DYNAMIC_ROUTING_TASK1_PRO: None,
                self._nsb.lims_project.DYNAMIC_ROUTING_TASK2_PRO: None,
                self._nsb.lims_project.DYNAMIC_ROUTING_ULTRA_OPT: None,
                self._nsb.lims_project.H120: None,
                self._nsb.lims_project.H200: None,
                self._nsb.lims_project.H301: None,
                self._nsb.lims_project.H301T: None,
                self._nsb.lims_project.H301_X: None,
                self._nsb.lims_project.H501_X: None,
                self._nsb.lims_project.H504: None,
                self._nsb.lims_project.IS_IX: None,
                self._nsb.lims_project.LARGE_SCALE_VOLTAGE: None,
                self._nsb.lims_project.LEARNINGM_FISH_DEVELOPMEN: None,
                self._nsb.lims_project.LEARNINGM_FISH_TASK1_A: None,
                self._nsb.lims_project.M301T: None,
                self._nsb.lims_project.MESOSCOPE_DEVELOPMENT: None,
                self._nsb.lims_project.M_FISH_PLATFORM_DEVELOPME: None,
                self._nsb.lims_project.MINDSCOPE_TRANSGENIC_CHAR: None,
                self._nsb.lims_project.M_IVSCCMET: None,
                self._nsb.lims_project.M_IVSCCME_TX: None,
                self._nsb.lims_project.M_M_PATCHX: None,
                self._nsb.lims_project.M_MPATC_HX: None,
                self._nsb.lims_project.MOUSE_BRAIN_CELL_ATLAS_CH: None,
                self._nsb.lims_project.MOUSE_BRAIN_CELL_ATLA_001: None,
                self._nsb.lims_project.MOUSE_BRAIN_CELL_ATLAS_TR: None,
                self._nsb.lims_project.MOUSE_FULL_MORPHOLOGY_FMO: None,
                self._nsb.lims_project.MOUSE_GENETIC_TOOLS_PROJE: None,
                self._nsb.lims_project.M_VISPTAXLO: None,
                self._nsb.lims_project.MULTISCOPE_SIGNAL_NOISE: None,
                self._nsb.lims_project.N200: None,
                self._nsb.lims_project.N310: None,
                self._nsb.lims_project.NEUROPIXEL_VISUAL_BEHAVIO: None,
                self._nsb.lims_project.NEUROPIXEL_VISUAL_BEH_001: None,
                self._nsb.lims_project.NEUROPIXEL_VISUAL_CODING: None,
                self._nsb.lims_project.OLVSX: None,
                self._nsb.lims_project.OM_FIS_HCOREGISTRATIONPIL: None,
                self._nsb.lims_project.OM_FISH_CUX2_MESO: None,
                self._nsb.lims_project.OM_FISH_GAD2_MESO: None,
                self._nsb.lims_project.OM_FISH_GAD2_PILOT: None,
                self._nsb.lims_project.OM_FISH_RBP4_MESO: None,
                self._nsb.lims_project.OM_FISH_RORB_PILOT: None,
                self._nsb.lims_project.OM_FISHRO_BINJECTIONVIRUS: None,
                self._nsb.lims_project.OM_FISH_SST_MESO: None,
                self._nsb.lims_project.OPEN_SCOPE_DENDRITE_COUPL: None,
                self._nsb.lims_project.OPENSCOPE_DEVELOPMENT: None,
                self._nsb.lims_project.OPEN_SCOPE_ILLUSION: None,
                self._nsb.lims_project.OPEN_SCOPE_GLOBAL_LOCAL_O: None,
                self._nsb.lims_project.OPENSCOPE_GAMMA_PILOT: None,
                self._nsb.lims_project.OPENSCOPE_GAMMA_PRODUCTLO: None,
                self._nsb.lims_project.OPENSCOPELNJECTION_PILOT: None,
                self._nsb.lims_project.OPENSCOPE_MOTION_PLLOT: None,
                self._nsb.lims_project.OPENSCOPE_MOTION_PRODUCTI: None,
                self._nsb.lims_project.OPENSCOPE_MULTIPLEX_PILOT: None,
                self._nsb.lims_project.OPENSCOPE_MULTIPLEX_PRODU: None,
                self._nsb.lims_project.OPEN_SCOPE_SEQUENCE_LEARN: None,
                self._nsb.lims_project.OPEN_SCOPE_TEMPORAL_BARCO: None,
                self._nsb.lims_project.OPEN_SCOPE_VISION2_HIPPOC: None,
                self._nsb.lims_project.OPH5_X: None,
                self._nsb.lims_project.S200_C: None,
                self._nsb.lims_project.SLC6_A1_NEUROPIXEL: None,
                self._nsb.lims_project.SMART_SPIM_GENETIC_TOOLS: None,
                self._nsb.lims_project.SURGERY_X: None,
                self._nsb.lims_project.T301: None,
                self._nsb.lims_project.T301T: None,
                self._nsb.lims_project.T301_X: None,
                self._nsb.lims_project.T503: None,
                self._nsb.lims_project.T503_X: None,
                self._nsb.lims_project.T504: None,
                self._nsb.lims_project.T504_X: None,
                self._nsb.lims_project.T600: None,
                self._nsb.lims_project.T601: None,
                self._nsb.lims_project.T601_X: None,
                self._nsb.lims_project.TCYTX: None,
                self._nsb.lims_project.TASK_TRAINED_NETWORKS_MUL: None,
                self._nsb.lims_project.TASK_TRAINED_NETWORKS_NEU: None,
                self._nsb.lims_project.TEMPLETON_PSYCHEDELICS: None,
                self._nsb.lims_project.TEMPLETON_TTOC: None,
                self._nsb.lims_project.TINY_BLUE_DOT_BEHAVIOR: None,
                self._nsb.lims_project.U01_BFCT: None,
                self._nsb.lims_project.VARIABILITY_AIM1: None,
                self._nsb.lims_project.VARIABILITY_AIM1_PILOT: None,
                self._nsb.lims_project.VARIABILITY_SPONTANEOUS: None,
                self._nsb.lims_project.VI_DEEP_DIVE_EM_VOLUME: None,
                self._nsb.lims_project.VI_DEEPDLVE_DEEPSCOPE_PIE: None,
                self._nsb.lims_project.VIP_AXONAL_V1_PHASE1: None,
                self._nsb.lims_project.VIP_SOMATIC_V1_MESO: None,
                self._nsb.lims_project.VIP_SOMATIC_V1_PHASE1: None,
                self._nsb.lims_project.VIP_SOMATIC_V1_PHASE2: None,
                self._nsb.lims_project.VISUAL_BEHAVIOR: None,
                self._nsb.lims_project.VISUAL_BEHAVIOR_DEVELOPME: None,
                self._nsb.lims_project.VISUAL_BEHAVIOR_MULTISCOP: None,
                self._nsb.lims_project.VISUAL_BEHAVIOR_MULTI_001: None,
                self._nsb.lims_project.VISUAL_BEHAV_IOR_MULTISCO: None,
                self._nsb.lims_project.VISUAL_BEHAVIOR_TASK1_B: None,
            }.get(self._nsb.lims_project, None)
        )

    @property
    def aind_lims_taskflow(self) -> Optional[Any]:
        """Maps lims_taskflow to aind model"""
        return (
            None
            if self._nsb.lims_taskflow is None
            else {
                self._nsb.lims_taskflow.AIND_EPHYS_SURGERY_ONLY: None,
                self._nsb.lims_taskflow.AIND_EPHYS_PASSIVE_BEHAVI: None,
                self._nsb.lims_taskflow.AIND_U19_AAV_RETROGRADE: None,
                self._nsb.lims_taskflow.AIND_U19_RAB_V_RETROGRADE: None,
                self._nsb.lims_taskflow.AIND_U19_THALAMUS: None,
                self._nsb.lims_taskflow.AIND_WATERLOG: None,
                self._nsb.lims_taskflow.BRAIN_LARGE_SCALE_RECORDI: None,
                self._nsb.lims_taskflow.BRAIN_MOUSE_BRAIN_CELL_AT: None,
                self._nsb.lims_taskflow.BRAIN_OBSERVATORY_DEEPSCO: None,
                self._nsb.lims_taskflow.BRAIN_OBSERVATORY_EPHYS_D: None,
                self._nsb.lims_taskflow.BRAIN_OBSERVATORY_MAPSCOP: None,
                self._nsb.lims_taskflow.BRAIN_OBSERVATORY_MESOSCO: None,
                self._nsb.lims_taskflow.BRAIN_OBSERVATORY_MES_001: None,
                self._nsb.lims_taskflow.BRAIN_OBSERVATORY_NEUROPI: None,
                self._nsb.lims_taskflow.BRAIN_OBSERVATORY_TRANSGE: None,
                self._nsb.lims_taskflow.BRAIN_OBSERVATORY_V1_DD: None,
                self._nsb.lims_taskflow.BRAIN_OBSERVATORY_VISUAL: None,
                self._nsb.lims_taskflow.BRAIN_OBSERVATORY_VIS_001: None,
                self._nsb.lims_taskflow.BRAIN_OBSERVATORY_VIS_002: None,
                self._nsb.lims_taskflow.BRAIN_OBSERVATORY_VIS_003: None,
                self._nsb.lims_taskflow.BTV_BRAIN_VIRAL_STRATEGIE: None,
                self._nsb.lims_taskflow.CITRIC_ACID_PILOT: None,
                self._nsb.lims_taskflow.EPHYS_DEV_VISUAL_BEHAVIOR_2: None,
                self._nsb.lims_taskflow.EPHYS_DEV_VISUAL_BEHAVIOR: None,
                self._nsb.lims_taskflow.EPHYS_TASK_DEV_DYNAMIC_RO: None,
                self._nsb.lims_taskflow.EPHYS_TASK_DEV_DYANMIC_RO: None,
                self._nsb.lims_taskflow.EPHYS_TASK_DEV_DYNAMI_001: None,
                self._nsb.lims_taskflow.IVSCC_HVA_RETRO_PATCH_SEQ: None,
                self._nsb.lims_taskflow.IVSC_CM_INJECTION: None,
                self._nsb.lims_taskflow.IVSP_CM_INJECTION: None,
                self._nsb.lims_taskflow.MGT_LAB: None,
                self._nsb.lims_taskflow.MGT_TISSUE_CYTE: None,
                self._nsb.lims_taskflow.MINDSCOPE_2_P_TESTING: None,
                self._nsb.lims_taskflow.MSP_DYNAMIC_ROUTING_BEHAV: None,
                self._nsb.lims_taskflow.MSP_DYNAMIC_ROUTING_OPTO: None,
                self._nsb.lims_taskflow.MSP_DYNAMIC_ROUTING_SURGI: None,
                self._nsb.lims_taskflow.MSP_DYNAMIC_ROUTING_ULTRA: None,
                self._nsb.lims_taskflow.MSP_DYNAMIC_ROUTING_TASK: None,
                self._nsb.lims_taskflow.MSP_DYNAMIC_ROUTING_T_001: None,
                self._nsb.lims_taskflow.MSP_G_CA_MP8_TESTING: None,
                self._nsb.lims_taskflow.MSP_G_CA_MP8_TESTING_RO: None,
                self._nsb.lims_taskflow.MSP_LEARNING_M_FISH_DEVEL: None,
                self._nsb.lims_taskflow.MSP_LEARNING_M_FISH_D_001: None,
                self._nsb.lims_taskflow.MSP_LEARNING_M_FISH_FRONT: None,
                self._nsb.lims_taskflow.MSP_LEARNING_M_FISH_VIRUS: None,
                self._nsb.lims_taskflow.MSP_OM_FISH_COREGISTRATIO: None,
                self._nsb.lims_taskflow.MSP_OM_FISH_CUX2_PILOT: None,
                self._nsb.lims_taskflow.MSP_OM_FISH_GAD2_MESO: None,
                self._nsb.lims_taskflow.MSP_OM_FISH_GAD2_PILOT: None,
                self._nsb.lims_taskflow.MSP_OM_FISH_RBP4_MESO: None,
                self._nsb.lims_taskflow.MSP_OM_FISH_RORB_PILOT: None,
                self._nsb.lims_taskflow.MSP_OM_FISH_ROB_INJECTION: None,
                self._nsb.lims_taskflow.MSP_OM_FISH_SST_MESO_GAMM: None,
                self._nsb.lims_taskflow.MSP_OM_FISH_VIP_MESO_GAMM: None,
                self._nsb.lims_taskflow.MSP_OPEN_SCOPE_DENDRITE_C: None,
                self._nsb.lims_taskflow.MSP_OPEN_SCOPE_ILLUSION: None,
                self._nsb.lims_taskflow.MSP_OPEN_SCOPE_GLOBAL_LOC: None,
                self._nsb.lims_taskflow.MSP_OPEN_SCOPE_GLOBAL_001: None,
                self._nsb.lims_taskflow.MSP_TASK_TRAINED_NETWORKS: None,
                self._nsb.lims_taskflow.MSP_TASK_TRAINED_NETW_001: None,
                self._nsb.lims_taskflow.MSP_U01_BRIDGING_FUNCTION: None,
                self._nsb.lims_taskflow.MSP_VARIABILITY_AIM_1: None,
                self._nsb.lims_taskflow.MSP_VARIABILITY_AIM_1_PIL: None,
                self._nsb.lims_taskflow.MSP_VARIABILITY_SPONTANEO: None,
                self._nsb.lims_taskflow.MSP_VIP_AXONAL_V1: None,
                self._nsb.lims_taskflow.MSP_VIP_SOMATIC_V1: None,
                self._nsb.lims_taskflow.OPENSCOPE_MOTION_PRODUCTI: None,
                self._nsb.lims_taskflow.OPENSCOPE_VIRUS_VALIDATIO: None,
                self._nsb.lims_taskflow.OPEN_SCOPE_GAMMA_PILOT: None,
                self._nsb.lims_taskflow.OPEN_SCOPE_GAMMA_PRODUCTI: None,
                self._nsb.lims_taskflow.OPEN_SCOPE_LNJECTION_VOLU: None,
                self._nsb.lims_taskflow.OPEN_SCOPE_MOTION_PILOT: None,
                self._nsb.lims_taskflow.OPEN_SCOPE_MULTIPLEX_PILO: None,
                self._nsb.lims_taskflow.OPEN_SCOPE_MULTIPLEX__001: None,
                self._nsb.lims_taskflow.OPEN_SCOPE_MULTIPLEX_PROD: None,
                self._nsb.lims_taskflow.OPEN_SCOPE_MULTLPLEX_PROD: None,
                self._nsb.lims_taskflow.OPEN_SCOPE_SEQUENCE_LEARN: None,
                self._nsb.lims_taskflow.OPEN_SCOPE_TEMPORAL_BARCO: None,
                self._nsb.lims_taskflow.OPEN_SCOPE_TEMPORAL_B_001: None,
                self._nsb.lims_taskflow.OPEN_SCOPE_VISION_2_HIPPO: None,
                self._nsb.lims_taskflow.OPEN_SCOPE_WHC_2_P_DEV: None,
                self._nsb.lims_taskflow.TEMPLETON_PSYCHEDELICS: None,
                self._nsb.lims_taskflow.TINY_BLUE_DOT_BEHAVIOR: None,
                self._nsb.lims_taskflow.TRANSGENIC_CHARACTERIZATI: None,
                self._nsb.lims_taskflow.VIS_B_DEV_CONTROL_GROUP: None,
                self._nsb.lims_taskflow.VIS_B_LATERAL_PREP_DEVELO: None,
                self._nsb.lims_taskflow.VIS_B_TASK_2_DEVELOPMENT: None,
                self._nsb.lims_taskflow.VGT_ENHANCERS_TRANSSYNAPT: None,
            }.get(self._nsb.lims_taskflow, None)
        )

    @property
    def aind_long_requestor_comments(self) -> Optional[str]:
        """Maps long_requestor_comments to aind model"""
        return self._nsb.long_requestor_comments

    @property
    def aind_ml2nd_inj(self) -> Optional[Decimal]:
        """Maps ml2nd_inj to aind model"""
        return self._map_float_to_decimal(self._nsb.ml2nd_inj)

    @property
    def aind_modified(self) -> Optional[datetime]:
        """Maps modified to aind model"""
        return self._nsb.modified

    @property
    def aind_nanoject_number_inj10(self) -> Optional[str]:
        """Maps nanoject_number_inj10 to aind model"""
        return (
            None
            if self._nsb.nanoject_number_inj10 is None
            else {
                self._nsb.nanoject_number_inj10.SELECT: None,
                self._nsb.nanoject_number_inj10.NJ1: (
                    self._nsb.nanoject_number_inj10.NJ1.value
                ),
                self._nsb.nanoject_number_inj10.NJ2: (
                    self._nsb.nanoject_number_inj10.NJ2.value
                ),
                self._nsb.nanoject_number_inj10.NJ3: (
                    self._nsb.nanoject_number_inj10.NJ3.value
                ),
                self._nsb.nanoject_number_inj10.NJ4: (
                    self._nsb.nanoject_number_inj10.NJ4.value
                ),
                self._nsb.nanoject_number_inj10.NJ5: (
                    self._nsb.nanoject_number_inj10.NJ5.value
                ),
                self._nsb.nanoject_number_inj10.NJ6: (
                    self._nsb.nanoject_number_inj10.NJ6.value
                ),
                self._nsb.nanoject_number_inj10.NJ7: (
                    self._nsb.nanoject_number_inj10.NJ7.value
                ),
                self._nsb.nanoject_number_inj10.NJ8: (
                    self._nsb.nanoject_number_inj10.NJ8.value
                ),
                self._nsb.nanoject_number_inj10.NA: None,
            }.get(self._nsb.nanoject_number_inj10, None)
        )

    @property
    def aind_nanoject_number_inj2(self) -> Optional[str]:
        """Maps nanoject_number_inj2 to aind model"""
        return (
            None
            if self._nsb.nanoject_number_inj2 is None
            else {
                self._nsb.nanoject_number_inj2.SELECT: None,
                self._nsb.nanoject_number_inj2.NJ1: (
                    self._nsb.nanoject_number_inj2.NJ1.value
                ),
                self._nsb.nanoject_number_inj2.NJ2: (
                    self._nsb.nanoject_number_inj2.NJ2.value
                ),
                self._nsb.nanoject_number_inj2.NJ3: (
                    self._nsb.nanoject_number_inj2.NJ3.value
                ),
                self._nsb.nanoject_number_inj2.NJ4: (
                    self._nsb.nanoject_number_inj2.NJ4.value
                ),
                self._nsb.nanoject_number_inj2.NJ5: (
                    self._nsb.nanoject_number_inj2.NJ5.value
                ),
                self._nsb.nanoject_number_inj2.NJ6: (
                    self._nsb.nanoject_number_inj2.NJ6.value
                ),
                self._nsb.nanoject_number_inj2.NJ7: (
                    self._nsb.nanoject_number_inj2.NJ7.value
                ),
                self._nsb.nanoject_number_inj2.NJ8: (
                    self._nsb.nanoject_number_inj2.NJ8.value
                ),
                self._nsb.nanoject_number_inj2.NA: None,
            }.get(self._nsb.nanoject_number_inj2, None)
        )

    @property
    def aind_non_x002d_nsb_surgeon(self) -> Optional[bool]:
        """Maps non_x002d_nsb_surgeon to aind model"""
        return self._nsb.non_x002d_nsb_surgeon

    @property
    def aind_of_burr(self) -> Optional[int]:
        """Maps of_burr to aind model"""
        return (
            None
            if self._nsb.of_burr is None
            else {
                self._nsb.of_burr.SELECT: None,
                self._nsb.of_burr.N_1: 1,
                self._nsb.of_burr.N_2: 2,
                self._nsb.of_burr.N_3: 3,
                self._nsb.of_burr.N_4: 4,
                self._nsb.of_burr.N_5: 5,
                self._nsb.of_burr.N_6: 6,
            }.get(self._nsb.of_burr, None)
        )

    @property
    def aind_pedigree_name(self) -> Optional[str]:
        """Maps pedigree_name to aind model"""
        return self._nsb.pedigree_name

    @property
    def aind_procedure(self) -> Optional[NSBProcedure]:
        """Maps procedure to aind model"""
        return self._nsb.procedure

    @property
    def aind_procedure_family(self) -> Optional[NSBProcedureCategory]:
        """Maps procedure_family to aind model"""
        return self._nsb.procedure_family

    @property
    def aind_procedure_slots(self) -> Optional[Any]:
        """Maps procedure_slots to aind model"""
        return (
            None
            if self._nsb.procedure_slots is None
            else {
                self._nsb.procedure_slots.SELECT: None,
                self._nsb.procedure_slots.SINGLE_SURGICAL_SESSION: None,
                self._nsb.procedure_slots.INITIAL_SURGERY_WITH_FOLL: None,
            }.get(self._nsb.procedure_slots, None)
        )

    @property
    def aind_procedure_t2(self) -> Optional[Any]:
        """Maps procedure_t2 to aind model"""
        return (
            None
            if self._nsb.procedure_t2 is None
            else {
                self._nsb.procedure_t2.SELECT: None,
                self._nsb.procedure_t2.N_2_P: None,
                self._nsb.procedure_t2.NP: None,
                self._nsb.procedure_t2.NA: None,
            }.get(self._nsb.procedure_t2, None)
        )

    @property
    def aind_project_id(self) -> Optional[Any]:
        """Maps project_id to aind model"""
        return (
            None
            if self._nsb.project_id is None
            else {
                self._nsb.project_id.N_1010300110_COSTA_PGA_LA: None,
                self._nsb.project_id.N_1020100710_CTY_M_FISH: None,
                self._nsb.project_id.N_1020100910_CTY_MORPHOLO: None,
                self._nsb.project_id.N_1020101110_CTY_CONNECTO: None,
                self._nsb.project_id.N_1020101210_CTY_CONNECTO: None,
                self._nsb.project_id.N_1020101610_CTY_TAXONOMY: None,
                self._nsb.project_id.N_1020102720_CTY_BRAIN_AX: None,
                self._nsb.project_id.N_1020102920_CTY_BRAIN_CE: None,
                self._nsb.project_id.N_1020103120_W4_CTY_EU_HO: None,
                self._nsb.project_id.N_1020103120_W5_CTY_EU_HO: None,
                self._nsb.project_id.N_1020103220_CTY_MOUSE_AG: None,
                self._nsb.project_id.N_1020103620_CTY_DISSEMIN: None,
                self._nsb.project_id.N_1020104020_CTY_BRAIN_UG: None,
                self._nsb.project_id.N_1020104320_CTY_OPTICAL: None,
                self._nsb.project_id.N_1020104410_CTY_GENOMICS: None,
                self._nsb.project_id.N_1020104510_CTY_IVSCC: None,
                self._nsb.project_id.N_1020104620_CTY_WEILL_NE: None,
                self._nsb.project_id.N_1020104810_CTY_BARCODED: None,
                self._nsb.project_id.N_1020104920_CTY_OPIOID_T: None,
                self._nsb.project_id.N_1020105520_CTY_EM_MOTOR: None,
                self._nsb.project_id.N_1020105720_CTY_BRAIN_BG: None,
                self._nsb.project_id.N_1020105920_CTY_SCORCH: None,
                self._nsb.project_id.N_1020106020_CTY_BRAIN_DR: None,
                self._nsb.project_id.N_1020106120_CTY_BICAN_HU: None,
                self._nsb.project_id.N_1020106220_CTY_BICAN_MO: None,
                self._nsb.project_id.N_1020106410_CTY_GENETIC: None,
                self._nsb.project_id.N_1020106620_CTY_CONNECTS: None,
                self._nsb.project_id.N_1020106820_CTY_CONNECTS: None,
                self._nsb.project_id.N_1020106920_PRE_SPEND: None,
                self._nsb.project_id.N_1020199910_CTY_PROGRAM: None,
                self._nsb.project_id.N_1020200410_BTV_VISUAL_B: None,
                self._nsb.project_id.N_1020201220_BTV_BRAIN_VI: None,
                self._nsb.project_id.N_1020201620_MSP_BRAIN_MO: None,
                self._nsb.project_id.N_1020201720_BTV_BRAIN_NE: None,
                self._nsb.project_id.N_1020400410_OTH_MERITORI: None,
                self._nsb.project_id.N_1020400620_OTH_MEASURIN: None,
                self._nsb.project_id.N_1020400710_APLD_TARGETE: None,
                self._nsb.project_id.N_1020401010_CTY_SR_SLC6: None,
                self._nsb.project_id.N_1020401110_CTY_SR_SYNGA: None,
                self._nsb.project_id.N_1020401210_CTY_SR_FRIED: None,
                self._nsb.project_id.N_1020401410_CTY_PARKINSO: None,
                self._nsb.project_id.N_1028800310_ANIMAL_CARE: None,
                self._nsb.project_id.N_1028800510_TRANSGENIC_C: None,
                self._nsb.project_id.N_1028800810_LAB_ANIMAL_S: None,
                self._nsb.project_id.N_1060100110_IMMUNOLOGY_D: None,
                self._nsb.project_id.N_1210101620_MSP_BRAIN_OP: None,
                self._nsb.project_id.N_1210101820_MSP_EPHAPTIC: None,
                self._nsb.project_id.N_1210102320_MSP_TEMPLETO: None,
                self._nsb.project_id.N_1210102520_MSP_U01_BRID: None,
                self._nsb.project_id.N_1210102620_MSP_TEMPLETO: None,
                self._nsb.project_id.N_1220100110_AIND_SCIENTI: None,
                self._nsb.project_id.N_1220100220_MOLECULAR_CO: None,
                self._nsb.project_id.N_1220100220_PROJECT_1: None,
                self._nsb.project_id.N_1220100220_PROJECT_2: None,
                self._nsb.project_id.N_1220100220_PROJECT_4: None,
                self._nsb.project_id.N_1220100420_AIND_BRAINST: None,
                self._nsb.project_id.N_1220101020_AIND_POO_SIM: None,
                self._nsb.project_id.N_1220101120_AIND_COHEN_J: None,
                self._nsb.project_id.N_1220101220_AIND_RF1_FUN: None,
                self._nsb.project_id.N_1220101420_AIND_SIEGLE: None,
                self._nsb.project_id.N_1220101310_MSP_SCIENTIF: None,
                self._nsb.project_id.N_1229999910_NEURAL_DYNAM: None,
                self._nsb.project_id.AAV_PRODUCTION_1028800410: None,
                self._nsb.project_id.RD_1028800410: None,
                # deleted options
                self._nsb.project_id.N_1210199910_MSP_CROSS_PR: None,
                self._nsb.project_id.N_1210199910_MSP_CROS_001: None,
                self._nsb.project_id.N_1210100110_MSP_DEEP_INT: None,
                self._nsb.project_id.N_1210100210_MSP_BEHAVIOR: None,
                self._nsb.project_id.N_1210100310_MSP_X_AREA_F: None,
                self._nsb.project_id.N_1210100410_MSP_VIP_REGU: None,
                self._nsb.project_id.N_1210100510_MSP_SURROUND: None,
                self._nsb.project_id.N_1210100610_MSP_AUTOMATI: None,
                self._nsb.project_id.N_1210100710_MSP_TASK_TRA: None,
                self._nsb.project_id.N_1210100810_MSP_NEURAL_E: None,
                self._nsb.project_id.N_1210100910_MSP_BIO_REAL: None,
                self._nsb.project_id.N_1210101010_MSP_V1_OM_FI: None,
                self._nsb.project_id.N_1210101110_MSP_DYNAMIC: None,
                self._nsb.project_id.N_1210101210_MSP_LEARNING: None,
                self._nsb.project_id.N_1210101420_MSP_BRAIN_MO: None,
                self._nsb.project_id.N_1210101510_MSP_FALCONWO: None,
            }.get(self._nsb.project_id, None)
        )

    @property
    def aind_ret_setting0(self) -> Optional[Any]:
        """Maps ret_setting0 to aind model"""
        return (
            None
            if self._nsb.ret_setting0 is None
            else {
                self._nsb.ret_setting0.OFF: None,
                self._nsb.ret_setting0.ON: None,
            }.get(self._nsb.ret_setting0, None)
        )

    @property
    def aind_ret_setting1(self) -> Optional[Any]:
        """Maps ret_setting1 to aind model"""
        return (
            None
            if self._nsb.ret_setting1 is None
            else {
                self._nsb.ret_setting1.OFF: None,
                self._nsb.ret_setting1.ON: None,
            }.get(self._nsb.ret_setting1, None)
        )

    @property
    def aind_round1_inj_isolevel(self) -> Optional[Decimal]:
        """Maps round1_inj_isolevel to aind model"""
        return self._map_float_to_decimal(self._nsb.round1_inj_isolevel)

    @property
    def aind_sex(self) -> Optional[Sex]:
        """Maps sex to aind model"""
        return (
            None
            if self._nsb.sex is None
            else {
                self._nsb.sex.SELECT: None,
                self._nsb.sex.MALE: Sex.MALE,
                self._nsb.sex.FEMALE: Sex.FEMALE,
            }.get(self._nsb.sex, None)
        )

    @property
    def aind_surgery_status(self) -> Optional[Any]:
        """Maps surgery_status to aind model"""
        return (
            None
            if self._nsb.surgery_status is None
            else {
                self._nsb.surgery_status.NEW: None,
                self._nsb.surgery_status.INJECTION_PENDING: None,
                self._nsb.surgery_status.PHASE_2_PENDING: None,
                self._nsb.surgery_status.READY_FOR_FEEDBACK: None,
                self._nsb.surgery_status.UNPLANNED_ACUTE: None,
                self._nsb.surgery_status.PLANNED_ACUTE: None,
                self._nsb.surgery_status.NO_SURGERY: None,
            }.get(self._nsb.surgery_status, None)
        )

    @property
    def aind_title(self) -> Optional[str]:
        """Maps title to aind model"""
        return self._nsb.title

    @property
    def aind_ui_version_string(self) -> Optional[str]:
        """Maps ui_version_string to aind model"""
        return self._nsb.ui_version_string

    @property
    def aind_virus_a_p(self) -> Optional[Decimal]:
        """Maps virus_a_p to aind model"""
        return self._map_float_to_decimal(self._nsb.virus_a_p)

    @property
    def aind_virus_d_v(self) -> Optional[Decimal]:
        """Maps virus_d_v to aind model"""
        return self._map_float_to_decimal(self._nsb.virus_d_v)

    @property
    def aind_virus_hemisphere(self) -> Optional[Side]:
        """Maps virus_hemisphere to aind model"""
        return (
            None
            if self._nsb.virus_hemisphere is None
            else {
                self._nsb.virus_hemisphere.SELECT: None,
                self._nsb.virus_hemisphere.LEFT: Side.LEFT,
                self._nsb.virus_hemisphere.RIGHT: Side.RIGHT,
            }.get(self._nsb.virus_hemisphere, None)
        )

    @property
    def aind_virus_m_l(self) -> Optional[Decimal]:
        """Maps virus_m_l to aind model"""
        return self._map_float_to_decimal(self._nsb.virus_m_l)

    @property
    def aind_weight_after_surgery(self) -> Optional[Decimal]:
        """Maps weight_after_surgery to aind model"""
        return self._map_float_to_decimal(self._nsb.weight_after_surgery)

    @property
    def aind_weight_before_surger(self) -> Optional[Decimal]:
        """Maps weight_before_surger to aind model"""
        return self._map_float_to_decimal(self._nsb.weight_before_surger)

    @property
    def aind_work_station1st_injection(self) -> Optional[str]:
        """Maps work_station1st_injection to aind model"""
        return (
            None
            if self._nsb.work_station1st_injection is None
            else {
                self._nsb.work_station1st_injection.SELECT: None,
                self._nsb.work_station1st_injection.SWS_1: (
                    self._nsb.work_station1st_injection.SWS_1.value
                ),
                self._nsb.work_station1st_injection.SWS_2: (
                    self._nsb.work_station1st_injection.SWS_2.value
                ),
                self._nsb.work_station1st_injection.SWS_3: (
                    self._nsb.work_station1st_injection.SWS_3.value
                ),
                self._nsb.work_station1st_injection.SWS_4: (
                    self._nsb.work_station1st_injection.SWS_4.value
                ),
                self._nsb.work_station1st_injection.SWS_5: (
                    self._nsb.work_station1st_injection.SWS_5.value
                ),
                self._nsb.work_station1st_injection.SWS_6: (
                    self._nsb.work_station1st_injection.SWS_6.value
                ),
                self._nsb.work_station1st_injection.SWS_7: (
                    self._nsb.work_station1st_injection.SWS_7.value
                ),
                self._nsb.work_station1st_injection.SWS_8: (
                    self._nsb.work_station1st_injection.SWS_8.value
                ),
                self._nsb.work_station1st_injection.SWS_9: (
                    self._nsb.work_station1st_injection.SWS_9.value
                ),
            }.get(self._nsb.work_station1st_injection, None)
        )

    # Additional Properties
    @property
    def aind_experimenter_full_name(self) -> str:
        """Map author id to experimenter name"""
        return (
            "NSB"
            if self.aind_author_id is None
            else f"NSB-{self.aind_author_id}"
        )

    def has_hp_procedure(self) -> bool:
        """Is there a headpost procedure?"""
        return self.aind_procedure in {
            NSBProcedure.HP_ONLY,
            NSBProcedure.HP_TRANSCRANIAL,
            NSBProcedure.FIBER_OPTIC_IMPLANT_WITH,
            NSBProcedure.INJECTION_FIBER_OPTIC_IMP,
            NSBProcedure.ISIGUIDED_INJECTION_WITH,
            NSBProcedure.STEREOTAXIC_INJECTION_WIT,
        }

    def has_cran_procedure(self) -> bool:
        """Is there a craniotomy procedure?"""
        return self.aind_procedure in {
            NSBProcedure.FRONTAL_CTX_2_P,
            NSBProcedure.INJ_MOTOR_CTX,
            NSBProcedure.INJ_VISUAL_CTX_2_P,
            NSBProcedure.INJ_WHC_NP_1_INJECTION_LO,
            NSBProcedure.MOTOR_CTX,
            NSBProcedure.VISUAL_CTX_NP,
            NSBProcedure.VISUAL_CTX_2_P,
            NSBProcedure.WHC_NP,
        }

    def surgery_during_info(
        self, during: During, inj_type: Optional[InjectionType] = None
    ) -> SurgeryDuringInfo:
        """
        Compiles burr hole information from NSB data
        Parameters
        ----------
        during : During
          Initial or Follow up
        inj_type : Optional[InjectionType]
          Injection type during the surgery. Default is None.

        Returns
        -------
        SurgeryDuringInfo

        """
        if during == During.FOLLOW_UP:
            if inj_type == InjectionType.NANOJECT:
                instrument_id = self.aind_nanoject_number_inj2
            elif inj_type == InjectionType.IONTOPHORESIS:
                instrument_id = self.aind_ionto_number_inj2
            else:
                instrument_id = None
            # backend fields titled "1st injection" correlate with followup
            # procedures
            return SurgeryDuringInfo(
                anaesthetic_duration_in_minutes=(
                    self.aind_first_injection_iso_durat
                ),
                anaesthetic_level=self.aind_round1_inj_isolevel,
                start_date=self.aind_date1st_injection,
                workstation_id=self.aind_work_station1st_injection,
                recovery_time=self.aind_first_inj_recovery,
                weight_prior=self.aind_first_injection_weight_be,
                weight_post=self.aind_first_injection_weight_af,
                instrument_id=instrument_id,
            )
        elif during == During.INITIAL:
            if inj_type == InjectionType.NANOJECT:
                instrument_id = self.aind_nanoject_number_inj10
            elif inj_type == InjectionType.IONTOPHORESIS:
                instrument_id = self.aind_ionto_number_inj1
            else:
                instrument_id = None
            # backend fields titled "HP" correlate with initial procedures
            return SurgeryDuringInfo(
                anaesthetic_duration_in_minutes=self.aind_iso_on,
                anaesthetic_level=self.aind_hp_iso_level,
                start_date=self.aind_date_of_surgery,
                workstation_id=self.aind_hp_work_station,
                recovery_time=self.aind_hp_recovery,
                weight_prior=self.aind_weight_before_surger,
                weight_post=self.aind_weight_after_surgery,
                instrument_id=instrument_id,
            )
        else:
            return SurgeryDuringInfo()

    def burr_hole_info(self, burr_hole_num: int) -> BurrHoleInfo:
        """
        Compiles burr hole information from NSB data
        Parameters
        ----------
        burr_hole_num : int
          Burr hole number

        Returns
        -------
        BurrHoleInfo

        """
        if burr_hole_num == 1:
            coordinate_depth = self._map_burr_hole_dv(
                self.aind_virus_d_v,
                self.aind_burr_1_d_v_x00,
                self.aind_burr_1_dv_2,
            )
            injectable_materials = self._pair_burr_hole_inj_materials(
                materials=[
                    self.aind_burr_1_injectable_x0,
                    self.aind_burr_1_injectable_x00,
                    self.aind_burr_1_injectable_x01,
                    self.aind_burr_1_injectable_x02,
                ],
                titers=[
                    self.aind_burr_1_injectable_x03,
                    self.aind_burr_1_injectable_x04,
                    self.aind_burr_1_injectable_x05,
                    self.aind_burr_1_injectable_x06,
                ],
            )
            return BurrHoleInfo(
                hemisphere=self.aind_virus_hemisphere,
                coordinate_ml=self.aind_virus_m_l,
                coordinate_ap=self.aind_virus_a_p,
                coordinate_depth=coordinate_depth,
                angle=self.aind_inj1_angle_v2,
                during=self.aind_burr1_perform_during,
                inj_type=self.aind_inj1_type,
                virus_strain=self.aind_inj1_virus_strain_rt,
                inj_current=self.aind_inj1_current,
                alternating_current=self.aind_inj1_alternating_time,
                inj_duration=self.aind_inj1_ionto_time,
                inj_volume=self._map_burr_hole_volume(
                    vol=self.aind_inj1volperdepth, dv=coordinate_depth
                ),
                inj_materials=injectable_materials,
                fiber_implant_depth=self.aind_fiber_implant1_dv,
                fiber_type=self.aind_burr_1_fiber_t,
                fiber_implant_length=self.aind_fiber_implant1_lengt,
            )
        elif burr_hole_num == 2:
            coordinate_depth = self._map_burr_hole_dv(
                self.aind_dv2nd_inj,
                self.aind_burr_2_d_v_x00,
                self.aind_burr_2_d_v_x000,
            )
            injectable_materials = self._pair_burr_hole_inj_materials(
                materials=[
                    self.aind_burr_2_injectable_x0,
                    self.aind_burr_2_injectable_x00,
                    self.aind_burr_2_injectable_x01,
                    self.aind_burr_2_injectable_x02,
                ],
                titers=[
                    self.aind_burr_2_injectable_x03,
                    self.aind_burr_2_injectable_x04,
                    self.aind_burr_2_injectable_x05,
                    self.aind_burr_2_injectable_x06,
                ],
            )
            return BurrHoleInfo(
                hemisphere=self.aind_hemisphere2nd_inj,
                coordinate_ml=self.aind_ml2nd_inj,
                coordinate_ap=self.aind_ap2nd_inj,
                coordinate_depth=coordinate_depth,
                angle=self.aind_inj2_angle_v2,
                during=self.aind_burr2_perform_during,
                inj_type=self.aind_inj2_type,
                virus_strain=self.aind_inj2_virus_strain_rt,
                inj_current=self.aind_inj2_current,
                alternating_current=self.aind_inj2_alternating_time,
                inj_duration=self.aind_inj2_ionto_time,
                inj_volume=self._map_burr_hole_volume(
                    vol=self.aind_inj2volperdepth, dv=coordinate_depth
                ),
                inj_materials=injectable_materials,
                fiber_implant_depth=self.aind_fiber_implant2_dv,
                fiber_type=self.aind_burr_2_fiber_t,
                fiber_implant_length=self.aind_fiber_implant2_lengt,
            )
        elif burr_hole_num == 3:
            coordinate_depth = self._map_burr_hole_dv(
                self.aind_burr3_d_v,
                self.aind_burr_3_d_v_x00,
                self.aind_burr_3_d_v_x000,
            )
            injectable_materials = self._pair_burr_hole_inj_materials(
                materials=[
                    self.aind_burr_3_injectable_x0,
                    self.aind_burr_3_injectable_x00,
                    self.aind_burr_3_injectable_x01,
                    self.aind_burr_3_injectable_x02,
                ],
                titers=[
                    self.aind_burr_3_injectable_x03,
                    self.aind_burr_3_injectable_x04,
                    self.aind_burr_3_injectable_x05,
                    self.aind_burr_3_injectable_x06,
                ],
            )
            return BurrHoleInfo(
                hemisphere=self.aind_burr_3_hemisphere,
                coordinate_ml=self.aind_burr3_m_l,
                coordinate_ap=self.aind_burr3_a_p,
                coordinate_depth=coordinate_depth,
                angle=self.aind_burr_3_angle,
                during=self.aind_burr3_perform_during,
                inj_type=self.aind_inj3_type,
                virus_strain=self.aind_inj_virus_strain_rt,
                inj_current=self.aind_inj3_current,
                alternating_current=self.aind_inj3_alternating_time,
                inj_duration=self.aind_inj3_ionto_time,
                inj_volume=self._map_burr_hole_volume(
                    vol=self.aind_inj3volperdepth, dv=coordinate_depth
                ),
                inj_materials=injectable_materials,
                fiber_implant_depth=self.aind_fiber_implant3_d_x00,
                fiber_type=self.aind_burr_3_fiber_t,
                fiber_implant_length=self.aind_fiber_implant3_lengt,
            )
        elif burr_hole_num == 4:
            coordinate_depth = self._map_burr_hole_dv(
                self.aind_burr4_d_v,
                self.aind_burr_4_d_v_x00,
                self.aind_burr_4_d_v_x000,
            )
            injectable_materials = self._pair_burr_hole_inj_materials(
                materials=[
                    self.aind_burr_4_injectable_x0,
                    self.aind_burr_4_injectable_x00,
                    self.aind_burr_4_injectable_x01,
                    self.aind_burr_4_injectable_x02,
                ],
                titers=[
                    self.aind_burr_4_injectable_x03,
                    self.aind_burr_4_injectable_x04,
                    self.aind_burr_4_injectable_x05,
                    self.aind_burr_4_injectable_x06,
                ],
            )
            return BurrHoleInfo(
                hemisphere=self.aind_burr_4_hemisphere,
                coordinate_ml=self.aind_burr4_m_l,
                coordinate_ap=self.aind_burr4_a_p,
                coordinate_depth=coordinate_depth,
                angle=self.aind_burr_4_angle,
                during=self.aind_burr4_perform_during,
                inj_type=self.aind_inj4_type,
                virus_strain=self.aind_inj4_virus_strain_rt,
                inj_current=self.aind_inj4_current,
                alternating_current=self.aind_inj4_alternating_time,
                inj_duration=self.aind_inj4_ionto_time,
                inj_volume=self._map_burr_hole_volume(
                    vol=self.aind_inj4volperdepth, dv=coordinate_depth
                ),
                inj_materials=injectable_materials,
                fiber_implant_depth=self.aind_fiber_implant4_d_x00,
                fiber_type=self.aind_burr_4_fiber_t,
                fiber_implant_length=self.aind_fiber_implant4_lengt,
            )
        elif burr_hole_num == 5:
            coordinate_depth = self._map_burr_hole_dv(
                self.aind_burr_5_d_v_x00,
                self.aind_burr_5_d_v_x000,
                self.aind_burr_5_d_v_x001,
            )
            injectable_materials = self._pair_burr_hole_inj_materials(
                materials=[
                    self.aind_burr_5_injectable_x0,
                    self.aind_burr_5_injectable_x00,
                    self.aind_burr_5_injectable_x01,
                    self.aind_burr_5_injectable_x02,
                ],
                titers=[
                    self.aind_burr_5_injectable_x03,
                    self.aind_burr_5_injectable_x04,
                    self.aind_burr_5_injectable_x05,
                    self.aind_burr_5_injectable_x06,
                ],
            )
            return BurrHoleInfo(
                hemisphere=self.aind_burr_5_hemisphere,
                coordinate_ml=self.aind_burr_5_m_l,
                coordinate_ap=self.aind_burr_5_a_p,
                coordinate_depth=coordinate_depth,
                angle=self.aind_burr_5_angle,
                during=self.aind_burr5_perform_during,
                inj_type=self.aind_inj5_type,
                virus_strain=self.aind_inj5_virus_strain_rt,
                inj_current=self.aind_inj5_current,
                alternating_current=self.aind_inj5_alternating_time,
                inj_duration=self.aind_inj5_ionto_time,
                inj_volume=self._map_burr_hole_volume(
                    vol=self.aind_inj5volperdepth, dv=coordinate_depth
                ),
                inj_materials=injectable_materials,
                fiber_implant_depth=self.aind_fiber_implant5_d_x00,
                fiber_type=self.aind_burr_5_fiber_t,
                fiber_implant_length=self.aind_fiber_implant5_lengt,
            )
        elif burr_hole_num == 6:
            coordinate_depth = self._map_burr_hole_dv(
                self.aind_burr_6_d_v_x00,
                self.aind_burr_6_d_v_x000,
                self.aind_burr_6_d_v_x001,
            )
            injectable_materials = self._pair_burr_hole_inj_materials(
                materials=[
                    self.aind_burr_6_injectable_x0,
                    self.aind_burr_6_injectable_x00,
                    self.aind_burr_6_injectable_x01,
                    self.aind_burr_6_injectable_x02,
                ],
                titers=[
                    self.aind_burr_6_injectable_x03,
                    self.aind_burr_6_injectable_x04,
                    self.aind_burr_6_injectable_x05,
                    self.aind_burr_6_injectable_x06,
                ],
            )
            return BurrHoleInfo(
                hemisphere=self.aind_burr_6_hemisphere,
                coordinate_ml=self.aind_burr_6_m_l,
                coordinate_ap=self.aind_burr_6_a_p,
                coordinate_depth=coordinate_depth,
                angle=self.aind_burr_6_angle,
                during=self.aind_burr6_perform_during,
                inj_type=self.aind_inj6_type,
                virus_strain=self.aind_inj6_virus_strain_rt,
                inj_current=self.aind_inj6_current,
                alternating_current=self.aind_inj6_alternating_time,
                inj_duration=self.aind_inj6_ionto_time,
                inj_volume=self._map_burr_hole_volume(
                    vol=self.aind_inj6volperdepth, dv=coordinate_depth
                ),
                inj_materials=injectable_materials,
                fiber_implant_depth=self.aind_fiber_implant6_d_x00,
                fiber_type=self.aind_burr_6_fiber_t,
                fiber_implant_length=self.aind_fiber_implant6_lengt,
            )
        else:
            return BurrHoleInfo()

    @staticmethod
    def _map_burr_hole_dv(dv1, dv2, dv3):
        """Maps dvs for a burr hole to one coordinate depth list"""
        if all(dv is None for dv in (dv1, dv2, dv3)):
            return None
        else:
            return [dv for dv in (dv1, dv2, dv3) if dv is not None]

    @staticmethod
    def _map_burr_hole_volume(vol, dv):
        """Maps volume to a list per depth"""
        if vol is None and dv is None:
            return None
        elif vol is None:
            return None
        else:
            return [vol] * len(dv) if dv is not None else [vol]

    def map_burr_hole_injection_materials(
        self, injectable_materials: List[InjectableMaterial]
    ) -> Optional[List[Union[ViralMaterial, NonViralMaterial]]]:
        """Maps injection materials for burr hole."""
        injection_materials = []
        for injectable_material in injectable_materials:
            if (
                injectable_material.material
                and injectable_material.titer_str
                and self._is_titer(injectable_material.titer_str)
            ):
                titer = re.search(
                    self.SCIENTIFIC_NOTATION_REGEX,
                    injectable_material.titer_str,
                ).group(0)
                viral = ViralMaterial.model_construct(
                    name=injectable_material.material,
                    titer=self._parse_titer_str(titer),
                )
                injection_materials.append(viral)
            elif (
                injectable_material.material
                and injectable_material.titer_str
                and self._is_concentration(injectable_material.titer_str)
            ):
                concentration = re.search(
                    self.CONCENTRATION_REGEX, injectable_material.titer_str
                ).group(1)
                non_viral = NonViralMaterial.model_construct(
                    name=injectable_material.material,
                    concentration=self._parse_concentration_str(concentration),
                )
                injection_materials.append(non_viral)
        return injection_materials

    @staticmethod
    def _pair_burr_hole_inj_materials(
        materials: List[str], titers: List[str]
    ) -> Optional[List[InjectableMaterial]]:
        """Pairs materials and corresponding titers/concentrations."""
        injectable_materials = []
        for material, titer_str in zip(materials, titers):
            if titer_str:
                injectable_material = InjectableMaterial(
                    material=material, titer_str=titer_str
                )
            else:
                injectable_material = InjectableMaterial(material=material)
            injectable_materials.append(injectable_material)
        return injectable_materials

    def _map_burr_fiber_probe(self, burr_info: BurrHoleInfo) -> FiberProbe:
        """Constructs a fiber probe"""
        if burr_info.fiber_type == FiberType.STANDARD:
            return FiberProbe.model_construct(
                manufacturer=Organization.NEUROPHOTOMETRICS,
                core_diameter=200,
                numerical_aperture=0.37,
                ferrule_material=FerruleMaterial.CERAMIC,
                total_length=burr_info.fiber_implant_length,
            )
        elif burr_info.fiber_type == FiberType.CUSTOM:
            # if custom, specs are stored in requestor comments
            return FiberProbe.model_construct(
                total_length=burr_info.fiber_implant_length,
                notes=self.aind_long_requestor_comments,
            )
        else:
            return FiberProbe.model_construct(
                total_length=burr_info.fiber_implant_length,
            )

    @staticmethod
    def assign_fiber_probe_names(procedures: List) -> None:
        """Assigns ordered names to FiberProbe objects within each fiber implant"""
        all_probes = []
        for proc in procedures:
            if isinstance(proc, FiberImplant):
                all_probes.extend(proc.probes)

        # Sort all probes based on ap (descending) and ml (ascending)
        sorted_probes = sorted(
            all_probes,
            key=lambda probe: (
                -float(probe.stereotactic_coordinate_ap),
                float(probe.stereotactic_coordinate_ml),
            ),
        )
        for probe_index, probe in enumerate(sorted_probes):
            probe.ophys_probe.name = f"Fiber_{probe_index}"

        return None

    def get_procedure(self) -> List[Surgery]:
        """Get a List of Surgeries"""
        # Surgery info
        # TODO: start_date should be based on During class
        initial_start_date = self.aind_date_of_surgery
        initial_animal_weight_prior = self.aind_weight_before_surger
        initial_animal_weight_post = self.aind_weight_after_surgery

        followup_start_date = self.aind_date1st_injection
        followup_animal_weight_prior = self.aind_first_injection_weight_be
        followup_animal_weight_post = self.aind_first_injection_weight_af

        experimenter_full_name = self.aind_experimenter_full_name
        iacuc_protocol = self.aind_iacuc_protocol

        # The if statements below will override these Nones with something proper hopefully
        initial_anaesthesia = None
        followup_anaesthesia = None
        initial_workstation_id = None
        followup_workstation_id = None
        notes = None
        other_procedures = []
        initial_procedures = []
        followup_procedures = []

        # Check if any headframe procedures
        if self.has_hp_procedure():
            hp_during = self.aind_headpost_perform_dur
            hf_surgery_during_info = self.surgery_during_info(hp_during)
            headpost_info = HeadPostInfo.from_hp_and_hp_type(
                hp=self.aind_headpost, hp_type=self.aind_headpost_type
            )

            # Missing protocol_id
            headframe_procedure = Headframe.model_construct(
                headframe_type=headpost_info.headframe_type,
                headframe_part_number=headpost_info.headframe_part_number,
                well_type=headpost_info.well_type,
                well_part_number=headpost_info.well_part_number,
            )
            # add to respective surgery
            if hp_during == During.INITIAL:
                initial_anaesthesia = Anaesthetic.model_construct(
                    type="isoflurane",
                    duration=(
                        hf_surgery_during_info.anaesthetic_duration_in_minutes
                    ),
                    level=hf_surgery_during_info.anaesthetic_level,
                )
                initial_workstation_id = self.aind_hp_work_station
                initial_procedures.append(headframe_procedure)
            elif hp_during == During.FOLLOW_UP:
                followup_anaesthesia = Anaesthetic.model_construct(
                    type="isoflurane",
                    duration=(
                        hf_surgery_during_info.anaesthetic_duration_in_minutes
                    ),
                    level=hf_surgery_during_info.anaesthetic_level,
                )
                followup_workstation_id = self.aind_hp_work_station
                followup_procedures.append(headframe_procedure)
            else:
                other_procedures.append(headframe_procedure)

        # Check for craniotomy procedures
        if self.has_cran_procedure():
            craniotomy_type = self.aind_craniotomy_type
            cran_during = self.aind_craniotomy_perform_d
            cran_during_info = self.surgery_during_info(cran_during)
            bregma_to_lambda_distance = self.aind_breg2_lamb
            implant_part_number = self.aind_implant_id_coverslip_type
            if craniotomy_type == CraniotomyType.FIVE_MM:
                craniotomy_coordinates_reference = (
                    CoordinateReferenceLocation.LAMBDA
                )
                craniotomy_size = Decimal("5")
            elif craniotomy_type == CraniotomyType.THREE_MM:
                craniotomy_coordinates_reference = None
                craniotomy_size = Decimal("3")
            else:
                craniotomy_coordinates_reference = None
                craniotomy_size = None

            cran_procedure = Craniotomy.model_construct(
                craniotomy_type=craniotomy_type,
                craniotomy_size=craniotomy_size,
                recovery_time=cran_during_info.recovery_time,
                bregma_to_lambda_distance=bregma_to_lambda_distance,
                craniotomy_coordinates_reference=(
                    craniotomy_coordinates_reference
                ),
                implant_part_number=implant_part_number,
            )
            headpost_info = HeadPostInfo.from_hp_and_hp_type(
                hp=self.aind_headpost, hp_type=self.aind_headpost_type
            )

            # all craniotomies are done with headframe.
            headframe_procedure = Headframe.model_construct(
                headframe_type=headpost_info.headframe_type,
                headframe_part_number=headpost_info.headframe_part_number,
                well_type=headpost_info.well_type,
                well_part_number=headpost_info.well_part_number,
            )

            if cran_during == During.INITIAL:
                initial_anaesthesia = Anaesthetic.model_construct(
                    type="isoflurane",
                    duration=cran_during_info.anaesthetic_duration_in_minutes,
                    level=cran_during_info.anaesthetic_level,
                )
                initial_workstation_id = self.aind_hp_work_station
                initial_procedures.append(cran_procedure)
                initial_procedures.append(headframe_procedure)
            elif cran_during == During.FOLLOW_UP:
                followup_anaesthesia = Anaesthetic.model_construct(
                    type="isoflurane",
                    duration=cran_during_info.anaesthetic_duration_in_minutes,
                    level=cran_during_info.anaesthetic_level,
                )
                followup_workstation_id = self.aind_hp_work_station
                followup_procedures.append(cran_procedure)
                followup_procedures.append(headframe_procedure)
            else:
                other_procedures.append(cran_procedure)
                other_procedures.append(headframe_procedure)

        # Check if there are any procedures for burr holes 1 through 6
        for burr_hole_num in range(1, 7):
            if getattr(self, f"aind_burr_hole_{burr_hole_num}") in {
                BurrHoleProcedure.INJECTION,
                BurrHoleProcedure.INJECTION_FIBER_IMPLANT,
            }:
                burr_hole_info = self.burr_hole_info(
                    burr_hole_num=burr_hole_num
                )
                burr_during_info = self.surgery_during_info(
                    during=burr_hole_info.during,
                    inj_type=burr_hole_info.inj_type,
                )
                injection_materials = self.map_burr_hole_injection_materials(
                    burr_hole_info.inj_materials
                )
                if burr_hole_info.inj_type == InjectionType.IONTOPHORESIS:
                    injection_proc = IontophoresisInjection.model_construct(
                        injection_hemisphere=burr_hole_info.hemisphere,
                        injection_coordinate_ml=burr_hole_info.coordinate_ml,
                        injection_coordinate_ap=burr_hole_info.coordinate_ap,
                        injection_coordinate_depth=(
                            burr_hole_info.coordinate_depth
                        ),
                        injection_angle=burr_hole_info.angle,
                        injection_current=burr_hole_info.inj_current,
                        injection_duration=burr_hole_info.inj_duration,
                        alternating_current=burr_hole_info.alternating_current,
                        recovery_time=burr_during_info.recovery_time,
                        instrument_id=burr_during_info.instrument_id,
                        bregma_to_lambda_distance=self.aind_breg2_lamb,
                        injection_coordinate_reference=(
                            CoordinateReferenceLocation.BREGMA
                        ),
                        injection_materials=injection_materials,
                    )
                elif burr_hole_info.inj_type == InjectionType.NANOJECT:
                    injection_proc = NanojectInjection.model_construct(
                        injection_hemisphere=burr_hole_info.hemisphere,
                        injection_coordinate_ml=burr_hole_info.coordinate_ml,
                        injection_coordinate_ap=burr_hole_info.coordinate_ap,
                        injection_coordinate_depth=(
                            burr_hole_info.coordinate_depth
                        ),
                        injection_angle=burr_hole_info.angle,
                        injection_current=burr_hole_info.inj_current,
                        injection_duration=burr_hole_info.inj_duration,
                        injection_volume=burr_hole_info.inj_volume,
                        alternating_current=burr_hole_info.alternating_current,
                        recovery_time=burr_during_info.recovery_time,
                        instrument_id=burr_during_info.instrument_id,
                        bregma_to_lambda_distance=self.aind_breg2_lamb,
                        injection_coordinate_reference=(
                            CoordinateReferenceLocation.BREGMA
                        ),
                        injection_materials=injection_materials,
                    )
                else:
                    injection_proc = BrainInjection.model_construct(
                        injection_hemisphere=burr_hole_info.hemisphere,
                        injection_coordinate_ml=burr_hole_info.coordinate_ml,
                        injection_coordinate_ap=burr_hole_info.coordinate_ap,
                        injection_coordinate_depth=(
                            burr_hole_info.coordinate_depth
                        ),
                        injection_angle=burr_hole_info.angle,
                        injection_duration=burr_hole_info.inj_duration,
                        recovery_time=burr_during_info.recovery_time,
                        instrument_id=burr_during_info.instrument_id,
                        bregma_to_lambda_distance=self.aind_breg2_lamb,
                        injection_coordinate_reference=(
                            CoordinateReferenceLocation.BREGMA
                        ),
                        injection_materials=injection_materials,
                    )
                if burr_hole_info.during == During.INITIAL:
                    initial_anaesthesia = Anaesthetic.model_construct(
                        type="isoflurane",
                        duration=burr_during_info.anaesthetic_duration_in_minutes,
                        level=burr_during_info.anaesthetic_level,
                    )
                    initial_workstation_id = burr_during_info.workstation_id
                    initial_procedures.append(injection_proc)
                elif burr_hole_info.during == During.FOLLOW_UP:
                    followup_anaesthesia = Anaesthetic.model_construct(
                        type="isoflurane",
                        duration=burr_during_info.anaesthetic_duration_in_minutes,
                        level=burr_during_info.anaesthetic_level,
                    )
                    followup_workstation_id = burr_during_info.workstation_id
                    followup_procedures.append(injection_proc)
                else:
                    other_procedures.append(injection_proc)
            if getattr(self, f"aind_burr_hole_{burr_hole_num}") in {
                BurrHoleProcedure.FIBER_IMPLANT,
                BurrHoleProcedure.INJECTION_FIBER_IMPLANT,
            }:
                burr_hole_info = self.burr_hole_info(
                    burr_hole_num=burr_hole_num
                )
                burr_during_info = self.surgery_during_info(
                    during=burr_hole_info.during,
                    inj_type=burr_hole_info.inj_type,
                )
                bregma_to_lambda_distance = self.aind_breg2_lamb
                fiber_probe = self._map_burr_fiber_probe(burr_hole_info)
                ophys_probe = OphysProbe.model_construct(
                    ophys_probe=fiber_probe,
                    targeted_structure=None,
                    stereotactic_coordinate_ml=burr_hole_info.coordinate_ml,
                    stereotactic_coordinate_ap=burr_hole_info.coordinate_ap,
                    stereotactic_coordinate_dv=(
                        burr_hole_info.fiber_implant_depth
                    ),
                    angle=burr_hole_info.angle,
                    bregma_to_lambda_distance=bregma_to_lambda_distance,
                    stereotactic_coordinate_reference=(
                        CoordinateReferenceLocation.BREGMA
                    ),
                )
                fiber_implant_proc = FiberImplant.model_construct(
                    probes=[ophys_probe]
                )
                if burr_hole_info.during == During.INITIAL:
                    initial_anaesthesia = Anaesthetic.model_construct(
                        type="isoflurane",
                        duration=burr_during_info.anaesthetic_duration_in_minutes,
                        level=burr_during_info.anaesthetic_level,
                    )
                    initial_workstation_id = burr_during_info.workstation_id
                    initial_procedures.append(fiber_implant_proc)
                elif burr_hole_info.during == During.FOLLOW_UP:
                    followup_anaesthesia = Anaesthetic.model_construct(
                        type="isoflurane",
                        duration=burr_during_info.anaesthetic_duration_in_minutes,
                        level=burr_during_info.anaesthetic_level,
                    )
                    followup_workstation_id = burr_during_info.workstation_id
                    followup_procedures.append(fiber_implant_proc)
                else:
                    other_procedures.append(fiber_implant_proc)

        surgeries = []
        if initial_procedures:
            self.assign_fiber_probe_names(initial_procedures)
            initial_surgery = Surgery.model_construct(
                start_date=initial_start_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=initial_animal_weight_prior,
                animal_weight_post=initial_animal_weight_post,
                anaesthesia=initial_anaesthesia,
                workstation_id=initial_workstation_id,
                notes=notes,
                procedures=initial_procedures,
            )
            surgeries.append(initial_surgery)
        if followup_procedures:
            self.assign_fiber_probe_names(followup_procedures)
            followup_surgery = Surgery.model_construct(
                start_date=followup_start_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=followup_animal_weight_prior,
                animal_weight_post=followup_animal_weight_post,
                anaesthesia=followup_anaesthesia,
                workstation_id=followup_workstation_id,
                notes=notes,
                procedures=followup_procedures,
            )
            surgeries.append(followup_surgery)

        # any other mapped procedures without During info will be put into one surgery object
        if other_procedures:
            self.assign_fiber_probe_names(other_procedures)
            other_surgery = Surgery.model_construct(
                start_date=None,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=None,
                animal_weight_post=None,
                anaesthesia=None,
                workstation_id=None,
                notes=notes,
                procedures=other_procedures,
            )
            surgeries.append(other_surgery)

        # generic surgery model if non-procedure info is available
        if (
            len(other_procedures) == 0
            and len(initial_procedures) == 0
            and self.aind_date_of_surgery
        ):
            generic_surgery = Surgery.model_construct(
                start_date=self.aind_date_of_surgery,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=self.aind_weight_before_surger,
                animal_weight_post=self.aind_weight_after_surgery,
                procedures=[],
            )
            surgeries.append(generic_surgery)

        return surgeries

    @property
        def aind_item_child_count(self) -> Optional[str]:
            """Maps item_child_count to aind model."""
            return self._nsb.item_child_count

    @property
        def aind_burr_x0020_5_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__injec to aind model."""
            return self._nsb.burr_x0020_5_x0020__injec

    @property
        def aind_burr_x0020_5_x0020_intend(self) -> Optional[Any]:
            """Maps burr_x0020_5_x0020_intend to aind model."""
            return (
                None
                if self._nsb.burr_x0020_5_x0020_intend is None
                else {
                    self._nsb.burr_x0020_5_x0020_intend.N_A: None,
                    self._nsb.burr_x0020_5_x0020_intend.DOPAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend.SEROTONIN: None,
                    self._nsb.burr_x0020_5_x0020_intend.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_5_x0020_intend.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_5_x0020_intend.HISTAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend.GLUTAMATE: None,
                    self._nsb.burr_x0020_5_x0020_intend.GABA: None,
                    self._nsb.burr_x0020_5_x0020_intend.CALCIUM: None,
                    self._nsb.burr_x0020_5_x0020_intend.VOLTAGE: None,
                    self._nsb.burr_x0020_5_x0020_intend.CONTROL: None,
                }.get(self._nsb.burr_x0020_5_x0020_intend, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020_intend_001(self) -> Optional[Any]:
            """Maps burr_x0020_5_x0020_intend_001 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_5_x0020_intend_001 is None
                else {
                    self._nsb.burr_x0020_5_x0020_intend_001.N_A: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.DOPAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.SEROTONIN: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.HISTAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.GLUTAMATE: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.GABA: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.CALCIUM: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.VOLTAGE: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.CONTROL: None,
                }.get(self._nsb.burr_x0020_5_x0020_intend_001, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_5_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_5_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_5_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_5_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_5_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_5_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_5_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_5_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020_m_x002(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020_m_x002 to aind model."""
            return self._nsb.burr_x0020_5_x0020_m_x002

    @property
        def aind_burr_x0020_1_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_1_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_1_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_2_x0020__fiber.STANDARD__PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_2_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_2_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020__injec to aind model."""
            return self._nsb.burr_x0020_2_x0020__injec

    @property
        def aind_burr_x0020_4_x0020_intend_001(self) -> Optional[Any]:
            """Maps burr_x0020_4_x0020_intend_001 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_4_x0020_intend_001 is None
                else {
                    self._nsb.burr_x0020_4_x0020_intend_001.N_A: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.DOPAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.SEROTONIN: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.HISTAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.GLUTAMATE: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.GABA: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.CALCIUM: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.VOLTAGE: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.CONTROL: None,
                }.get(self._nsb.burr_x0020_4_x0020_intend_001, None)
            )
    
        @property
        def aind_burr_x0020_4_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_4_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_4_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_4_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_4_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_4_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_4_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_4_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_4_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_4_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__angle to aind model."""
            return self._nsb.burr_x0020_5_x0020__angle

    @property
        def aind_burr_x0020_1_x0020__injec_005(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__injec_005 to aind model."""
            return self._nsb.burr_x0020_1_x0020__injec_005

    @property
        def aind_burr_x0020_4_x0020__injec_003(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__injec_003 to aind model."""
            return self._nsb.burr_x0020_4_x0020__injec_003

    @property
        def aind_burr_x0020_2_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_2_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_2_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_2_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_2_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_3_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__angle to aind model."""
            return self._nsb.burr_x0020_3_x0020__angle

    @property
        def aind_burr_x0020_6_x0020_a_x002(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020_a_x002 to aind model."""
            return self._nsb.burr_x0020_6_x0020_a_x002

    @property
        def aind_is_record(self) -> Optional[str]:
            """Maps is_record to aind model."""
            return self._nsb.is_record

    @property
        def aind_burr_x0020_1_x0020__grid(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__grid to aind model."""
            return self._nsb.burr_x0020_1_x0020__grid

    @property
        def aind_burr_x0020_4_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__angle to aind model."""
            return self._nsb.burr_x0020_4_x0020__angle

    @property
        def aind_burr_x0020_5_x0020__injec_007(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__injec_007 to aind model."""
            return self._nsb.burr_x0020_5_x0020__injec_007

    @property
        def aind_burr_x0020_2_x0020__injec_006(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020__injec_006 to aind model."""
            return self._nsb.burr_x0020_2_x0020__injec_006

    @property
        def aind_burr_x0020_4_x0020_d_x002(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020_d_x002 to aind model."""
            return self._nsb.burr_x0020_4_x0020_d_x002

    @property
        def aind_burr_x0020_2_x0020__injec_004(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020__injec_004 to aind model."""
            return self._nsb.burr_x0020_2_x0020__injec_004

    @property
        def aind_burr_x0020_5_x0020__hemis(self) -> Optional[Any]:
            """Maps burr_x0020_5_x0020__hemis to aind model."""
            return (
                None
                if self._nsb.burr_x0020_5_x0020__hemis is None
                else {
                    self._nsb.burr_x0020_5_x0020__hemis.SELECT: None,
                    self._nsb.burr_x0020_5_x0020__hemis.LEFT: None,
                    self._nsb.burr_x0020_5_x0020__hemis.RIGHT: None,
                }.get(self._nsb.burr_x0020_5_x0020__hemis, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__injec to aind model."""
            return self._nsb.burr_x0020_5_x0020__injec

    @property
        def aind_headpost_x0020__perform_x(self) -> Optional[Any]:
            """Maps headpost_x0020__perform_x to aind model."""
            return (
                None
                if self._nsb.headpost_x0020__perform_x is None
                else {
                    self._nsb.headpost_x0020__perform_x.INITIAL__SURGERY: None,
                    self._nsb.headpost_x0020__perform_x.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.headpost_x0020__perform_x, None)
            )
    
        @property
        def aind_hemisphere2nd_inj(self) -> Optional[Any]:
            """Maps hemisphere2nd_inj to aind model."""
            return (
                None
                if self._nsb.hemisphere2nd_inj is None
                else {
                    self._nsb.hemisphere2nd_inj.SELECT: None,
                    self._nsb.hemisphere2nd_inj.LEFT: None,
                    self._nsb.hemisphere2nd_inj.RIGHT: None,
                }.get(self._nsb.hemisphere2nd_inj, None)
            )
    
        @property
        def aind_hp_iso_level(self) -> Optional[str]:
            """Maps hp_iso_level to aind model."""
            return self._nsb.hp_iso_level

    @property
        def aind_burr_x0020_3_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_3_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_3_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_3_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_3_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_4_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__angle to aind model."""
            return self._nsb.burr_x0020_4_x0020__angle

    @property
        def aind_burr1_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr1_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr1_x0020__virus_x0020 is None
                else {
                    self._nsb.burr1_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr1_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr2_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr2_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__injection_x0 is None
                else {
                    self._nsb.burr2_x0020__injection_x0.SELECT: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr2_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr2_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr2_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__perform_x002 is None
                else {
                    self._nsb.burr2_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr2_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr2_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr2_x0020__status(self) -> Optional[Any]:
            """Maps burr2_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__status is None
                else {
                    self._nsb.burr2_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr2_x0020__status, None)
            )
    
        @property
        def aind_burr2_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr2_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__virus_x0020 is None
                else {
                    self._nsb.burr2_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr2_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr3_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__injection_x0 is None
                else {
                    self._nsb.burr3_x0020__injection_x0.SELECT: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr3_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr3_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr3_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__perform_x002 is None
                else {
                    self._nsb.burr3_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr3_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr3_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr3_x0020__status(self) -> Optional[Any]:
            """Maps burr3_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__status is None
                else {
                    self._nsb.burr3_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr3_x0020__status, None)
            )
    
        @property
        def aind_burr3_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr3_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__virus_x0020 is None
                else {
                    self._nsb.burr3_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr3_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr3_x0020_a_x002f_p to aind model."""
            return self._nsb.burr3_x0020_a_x002f_p

    @property
        def aind_burr_x0020_4_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_4_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_4_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_4_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_4_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_4_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_4_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_4_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_4_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_4_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__angle to aind model."""
            return self._nsb.burr_x0020_5_x0020__angle

    @property
        def aind_burr_x0020_1_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__injec to aind model."""
            return self._nsb.burr_x0020_1_x0020__injec

    @property
        def aind_burr_x0020_6_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_6_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_6_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_6_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_6_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_6_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_6_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_6_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_6_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_6_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_6_x0020_m_x002(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020_m_x002 to aind model."""
            return self._nsb.burr_x0020_6_x0020_m_x002

    @property
        def aind_burr_x0020_2_x0020__injec_001(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020__injec_001 to aind model."""
            return self._nsb.burr_x0020_2_x0020__injec_001

    @property
        def aind_burr_x0020_5_x0020__injec_004(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__injec_004 to aind model."""
            return self._nsb.burr_x0020_5_x0020__injec_004

    @property
        def aind_burr4_x0020_m_x002f_l(self) -> Optional[str]:
            """Maps burr4_x0020_m_x002f_l to aind model."""
            return self._nsb.burr4_x0020_m_x002f_l

    @property
        def aind_burr_x0020_5_x0020__injec_002(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__injec_002 to aind model."""
            return self._nsb.burr_x0020_5_x0020__injec_002

    @property
        def aind_editor(self) -> Optional[str]:
            """Maps editor to aind model."""
            return self._nsb.editor

    @property
        def aind_burr2_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr2_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__injection_x0 is None
                else {
                    self._nsb.burr2_x0020__injection_x0.SELECT: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr2_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr2_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr2_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__perform_x002 is None
                else {
                    self._nsb.burr2_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr2_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr2_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr2_x0020__status(self) -> Optional[Any]:
            """Maps burr2_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__status is None
                else {
                    self._nsb.burr2_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr2_x0020__status, None)
            )
    
        @property
        def aind_burr2_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr2_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__virus_x0020 is None
                else {
                    self._nsb.burr2_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr2_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr3_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__injection_x0 is None
                else {
                    self._nsb.burr3_x0020__injection_x0.SELECT: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr3_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr3_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr3_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__perform_x002 is None
                else {
                    self._nsb.burr3_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr3_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr3_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr3_x0020__status(self) -> Optional[Any]:
            """Maps burr3_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__status is None
                else {
                    self._nsb.burr3_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr3_x0020__status, None)
            )
    
        @property
        def aind_burr3_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr3_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__virus_x0020 is None
                else {
                    self._nsb.burr3_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr3_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr3_x0020_a_x002f_p to aind model."""
            return self._nsb.burr3_x0020_a_x002f_p

    @property
        def aind_pi(self) -> Optional[str]:
            """Maps pi to aind model."""
            return self._nsb.pi

    @property
        def aind_burr_x0020_3_x0020__injec_001(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__injec_001 to aind model."""
            return self._nsb.burr_x0020_3_x0020__injec_001

    @property
        def aind_burr6_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr6_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__virus_x0020 is None
                else {
                    self._nsb.burr6_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr6_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_1_x0020__fiber.STANDARD_PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_1_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_1_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__grid(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__grid to aind model."""
            return self._nsb.burr_x0020_1_x0020__grid

    @property
        def aind_fiber_x0020__implant3_x00_001(self) -> Optional[str]:
            """Maps fiber_x0020__implant3_x00_001 to aind model."""
            return self._nsb.fiber_x0020__implant3_x00_001

    @property
        def aind_burr_x0020_3_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__injec to aind model."""
            return self._nsb.burr_x0020_3_x0020__injec

    @property
        def aind_burr6_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr6_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__perform_x002 is None
                else {
                    self._nsb.burr6_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr6_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr6_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr6_x0020__status(self) -> Optional[Any]:
            """Maps burr6_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__status is None
                else {
                    self._nsb.burr6_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr6_x0020__status, None)
            )
    
        @property
        def aind_burr6_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr6_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__virus_x0020 is None
                else {
                    self._nsb.burr6_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr6_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_1_x0020__fiber.STANDARD_PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_1_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_1_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__grid(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__grid to aind model."""
            return self._nsb.burr_x0020_1_x0020__grid

    @property
        def aind_burr3_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr3_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__injection_x0 is None
                else {
                    self._nsb.burr3_x0020__injection_x0.SELECT: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr3_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr3_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr3_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__perform_x002 is None
                else {
                    self._nsb.burr3_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr3_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr3_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr3_x0020__status(self) -> Optional[Any]:
            """Maps burr3_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__status is None
                else {
                    self._nsb.burr3_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr3_x0020__status, None)
            )
    
        @property
        def aind_burr3_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr3_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__virus_x0020 is None
                else {
                    self._nsb.burr3_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr3_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr3_x0020_a_x002f_p to aind model."""
            return self._nsb.burr3_x0020_a_x002f_p

    @property
        def aind_behavior_x0020__destinati(self) -> Optional[Any]:
            """Maps behavior_x0020__destinati to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__destinati is None
                else {
                    self._nsb.behavior_x0020__destinati.EPHYS: None,
                    self._nsb.behavior_x0020__destinati.OPHYS: None,
                    self._nsb.behavior_x0020__destinati.HSFP: None,
                    self._nsb.behavior_x0020__destinati.PERFUSION: None,
                    self._nsb.behavior_x0020__destinati.N_A: None,
                }.get(self._nsb.behavior_x0020__destinati, None)
            )
    
        @property
        def aind_behavior_x0020__fiber_x00(self) -> Optional[Any]:
            """Maps behavior_x0020__fiber_x00 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__fiber_x00 is None
                else {
                    self._nsb.behavior_x0020__fiber_x00.YES: None,
                    self._nsb.behavior_x0020__fiber_x00.NO: None,
                }.get(self._nsb.behavior_x0020__fiber_x00, None)
            )
    
        @property
        def aind_behavior_x0020__first_x00(self) -> Optional[Any]:
            """Maps behavior_x0020__first_x00 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__first_x00 is None
                else {
                    self._nsb.behavior_x0020__first_x00.N_1_1: None,
                    self._nsb.behavior_x0020__first_x00.N_1_2: None,
                    self._nsb.behavior_x0020__first_x00.N_2: None,
                    self._nsb.behavior_x0020__first_x00.N_3: None,
                    self._nsb.behavior_x0020__first_x00.N_4: None,
                    self._nsb.behavior_x0020__first_x00.N_5: None,
                    self._nsb.behavior_x0020__first_x00.N_6: None,
                    self._nsb.behavior_x0020__first_x00.FINAL: None,
                    self._nsb.behavior_x0020__first_x00.GRADUATED: None,
                    self._nsb.behavior_x0020__first_x00.N_A: None,
                }.get(self._nsb.behavior_x0020__first_x00, None)
            )
    
        @property
        def aind_behavior_x0020__first_x00_001(self) -> Optional[Any]:
            """Maps behavior_x0020__first_x00_001 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__first_x00_001 is None
                else {
                    self._nsb.behavior_x0020__first_x00_001.N_1_1: None,
                    self._nsb.behavior_x0020__first_x00_001.N_1_2: None,
                    self._nsb.behavior_x0020__first_x00_001.N_2: None,
                    self._nsb.behavior_x0020__first_x00_001.N_3: None,
                    self._nsb.behavior_x0020__first_x00_001.N_4: None,
                    self._nsb.behavior_x0020__first_x00_001.N_5: None,
                    self._nsb.behavior_x0020__first_x00_001.N_6: None,
                    self._nsb.behavior_x0020__first_x00_001.FINAL: None,
                    self._nsb.behavior_x0020__first_x00_001.GRADUATED: None,
                    self._nsb.behavior_x0020__first_x00_001.N_A: None,
                }.get(self._nsb.behavior_x0020__first_x00_001, None)
            )
    
        @property
        def aind_behavior_x0020__platform(self) -> Optional[Any]:
            """Maps behavior_x0020__platform to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__platform is None
                else {
                    self._nsb.behavior_x0020__platform.MINDSCOPE: None,
                    self._nsb.behavior_x0020__platform.FORAGING: None,
                    self._nsb.behavior_x0020__platform.VR: None,
                }.get(self._nsb.behavior_x0020__platform, None)
            )
    
        @property
        def aind_behavior_x0020__type(self) -> Optional[Any]:
            """Maps behavior_x0020__type to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__type is None
                else {
                    self._nsb.behavior_x0020__type.SELECT: None,
                    self._nsb.behavior_x0020__type.FORAGING: None,
                    self._nsb.behavior_x0020__type.FORAGING_FP: None,
                    self._nsb.behavior_x0020__type.WR__HAB: None,
                    self._nsb.behavior_x0020__type.HAB__ONLY: None,
                }.get(self._nsb.behavior_x0020__type, None)
            )
    
        @property
        def aind_behavior_x0020_fip_x0020(self) -> Optional[Any]:
            """Maps behavior_x0020_fip_x0020 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020_fip_x0020 is None
                else {
                    self._nsb.behavior_x0020_fip_x0020.N_A: None,
                    self._nsb.behavior_x0020_fip_x0020.NORMAL: None,
                    self._nsb.behavior_x0020_fip_x0020.AXON: None,
                }.get(self._nsb.behavior_x0020_fip_x0020, None)
            )
    
        @property
        def aind_black_x0020__cement(self) -> Optional[Any]:
            """Maps black_x0020__cement to aind model."""
            return (
                None
                if self._nsb.black_x0020__cement is None
                else {
                    self._nsb.black_x0020__cement.YES: None,
                    self._nsb.black_x0020__cement.NO: None,
                }.get(self._nsb.black_x0020__cement, None)
            )
    
        @property
        def aind_breg2_lamb(self) -> Optional[str]:
            """Maps breg2_lamb to aind model."""
            return self._nsb.breg2_lamb

    @property
        def aind_burr1_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr1_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr1_x0020__injection_x0 is None
                else {
                    self._nsb.burr1_x0020__injection_x0.SELECT: None,
                    self._nsb.burr1_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr1_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr1_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr1_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr1_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr1_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr1_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr1_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr1_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr1_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr1_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr1_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr1_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr1_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr1_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr1_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr1_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr1_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr1_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr1_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr1_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr1_x0020__perform_x002 is None
                else {
                    self._nsb.burr1_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr1_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr1_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr1_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr1_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr1_x0020__virus_x0020 is None
                else {
                    self._nsb.burr1_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr1_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr2_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr2_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__injection_x0 is None
                else {
                    self._nsb.burr2_x0020__injection_x0.SELECT: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr2_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr2_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr2_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__perform_x002 is None
                else {
                    self._nsb.burr2_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr2_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr2_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr2_x0020__status(self) -> Optional[Any]:
            """Maps burr2_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__status is None
                else {
                    self._nsb.burr2_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr2_x0020__status, None)
            )
    
        @property
        def aind_burr2_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr2_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__virus_x0020 is None
                else {
                    self._nsb.burr2_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr2_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr3_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__injection_x0 is None
                else {
                    self._nsb.burr3_x0020__injection_x0.SELECT: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr3_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr3_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr3_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__perform_x002 is None
                else {
                    self._nsb.burr3_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr3_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr3_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr3_x0020__status(self) -> Optional[Any]:
            """Maps burr3_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__status is None
                else {
                    self._nsb.burr3_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr3_x0020__status, None)
            )
    
        @property
        def aind_burr3_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr3_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__virus_x0020 is None
                else {
                    self._nsb.burr3_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr3_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr3_x0020_a_x002f_p to aind model."""
            return self._nsb.burr3_x0020_a_x002f_p

    @property
        def aind_burr_x0020_4_x0020_intend(self) -> Optional[Any]:
            """Maps burr_x0020_4_x0020_intend to aind model."""
            return (
                None
                if self._nsb.burr_x0020_4_x0020_intend is None
                else {
                    self._nsb.burr_x0020_4_x0020_intend.N_A: None,
                    self._nsb.burr_x0020_4_x0020_intend.DOPAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend.SEROTONIN: None,
                    self._nsb.burr_x0020_4_x0020_intend.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_4_x0020_intend.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_4_x0020_intend.HISTAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend.GLUTAMATE: None,
                    self._nsb.burr_x0020_4_x0020_intend.GABA: None,
                    self._nsb.burr_x0020_4_x0020_intend.CALCIUM: None,
                    self._nsb.burr_x0020_4_x0020_intend.VOLTAGE: None,
                    self._nsb.burr_x0020_4_x0020_intend.CONTROL: None,
                }.get(self._nsb.burr_x0020_4_x0020_intend, None)
            )
    
        @property
        def aind_burr_x0020_4_x0020_intend_001(self) -> Optional[Any]:
            """Maps burr_x0020_4_x0020_intend_001 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_4_x0020_intend_001 is None
                else {
                    self._nsb.burr_x0020_4_x0020_intend_001.N_A: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.DOPAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.SEROTONIN: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.HISTAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.GLUTAMATE: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.GABA: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.CALCIUM: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.VOLTAGE: None,
                    self._nsb.burr_x0020_4_x0020_intend_001.CONTROL: None,
                }.get(self._nsb.burr_x0020_4_x0020_intend_001, None)
            )
    
        @property
        def aind_burr_x0020_4_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_4_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_4_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_4_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_4_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_4_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_4_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_4_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_4_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_4_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_4_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__angle to aind model."""
            return self._nsb.burr_x0020_5_x0020__angle

    @property
        def aind_content_type(self) -> Optional[str]:
            """Maps content_type to aind model."""
            return self._nsb.content_type

    @property
        def aind_burr_x0020_1_x0020__spina(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020__spina to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020__spina is None
                else {
                    self._nsb.burr_x0020_1_x0020__spina.SELECT: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_C1_C2: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_C2_C3: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_C3_C4: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_C4_C5: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_C6_C7: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_C7_C8: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_C8_T1: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_T1_T2: None,
                }.get(self._nsb.burr_x0020_1_x0020__spina, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020_d_x002(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020_d_x002 to aind model."""
            return self._nsb.burr_x0020_1_x0020_d_x002

    @property
        def aind_burr_x0020_6_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_6_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_6_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_6_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_6_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_6_x0020_m_x002(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020_m_x002 to aind model."""
            return self._nsb.burr_x0020_6_x0020_m_x002

    @property
        def aind_burr_x0020_2_x0020_intend_001(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020_intend_001 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020_intend_001 is None
                else {
                    self._nsb.burr_x0020_2_x0020_intend_001.N_A: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.DOPAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.SEROTONIN: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.HISTAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.GLUTAMATE: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.GABA: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.CALCIUM: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.VOLTAGE: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.CONTROL: None,
                }.get(self._nsb.burr_x0020_2_x0020_intend_001, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_2_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_2_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_2_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_2_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_3_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__angle to aind model."""
            return self._nsb.burr_x0020_3_x0020__angle

    @property
        def aind_behavior_x0020__first_x00_001(self) -> Optional[Any]:
            """Maps behavior_x0020__first_x00_001 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__first_x00_001 is None
                else {
                    self._nsb.behavior_x0020__first_x00_001.N_1_1: None,
                    self._nsb.behavior_x0020__first_x00_001.N_1_2: None,
                    self._nsb.behavior_x0020__first_x00_001.N_2: None,
                    self._nsb.behavior_x0020__first_x00_001.N_3: None,
                    self._nsb.behavior_x0020__first_x00_001.N_4: None,
                    self._nsb.behavior_x0020__first_x00_001.N_5: None,
                    self._nsb.behavior_x0020__first_x00_001.N_6: None,
                    self._nsb.behavior_x0020__first_x00_001.FINAL: None,
                    self._nsb.behavior_x0020__first_x00_001.GRADUATED: None,
                    self._nsb.behavior_x0020__first_x00_001.N_A: None,
                }.get(self._nsb.behavior_x0020__first_x00_001, None)
            )
    
        @property
        def aind_behavior_x0020__platform(self) -> Optional[Any]:
            """Maps behavior_x0020__platform to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__platform is None
                else {
                    self._nsb.behavior_x0020__platform.MINDSCOPE: None,
                    self._nsb.behavior_x0020__platform.FORAGING: None,
                    self._nsb.behavior_x0020__platform.VR: None,
                }.get(self._nsb.behavior_x0020__platform, None)
            )
    
        @property
        def aind_behavior_x0020__type(self) -> Optional[Any]:
            """Maps behavior_x0020__type to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__type is None
                else {
                    self._nsb.behavior_x0020__type.SELECT: None,
                    self._nsb.behavior_x0020__type.FORAGING: None,
                    self._nsb.behavior_x0020__type.FORAGING_FP: None,
                    self._nsb.behavior_x0020__type.WR__HAB: None,
                    self._nsb.behavior_x0020__type.HAB__ONLY: None,
                }.get(self._nsb.behavior_x0020__type, None)
            )
    
        @property
        def aind_behavior_x0020_fip_x0020(self) -> Optional[Any]:
            """Maps behavior_x0020_fip_x0020 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020_fip_x0020 is None
                else {
                    self._nsb.behavior_x0020_fip_x0020.N_A: None,
                    self._nsb.behavior_x0020_fip_x0020.NORMAL: None,
                    self._nsb.behavior_x0020_fip_x0020.AXON: None,
                }.get(self._nsb.behavior_x0020_fip_x0020, None)
            )
    
        @property
        def aind_black_x0020__cement(self) -> Optional[Any]:
            """Maps black_x0020__cement to aind model."""
            return (
                None
                if self._nsb.black_x0020__cement is None
                else {
                    self._nsb.black_x0020__cement.YES: None,
                    self._nsb.black_x0020__cement.NO: None,
                }.get(self._nsb.black_x0020__cement, None)
            )
    
        @property
        def aind_breg2_lamb(self) -> Optional[str]:
            """Maps breg2_lamb to aind model."""
            return self._nsb.breg2_lamb

    @property
        def aind_fiber_x0020__implant4_x00_001(self) -> Optional[str]:
            """Maps fiber_x0020__implant4_x00_001 to aind model."""
            return self._nsb.fiber_x0020__implant4_x00_001

    @property
        def aind_burr_x0020_6_x0020__injec_002(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020__injec_002 to aind model."""
            return self._nsb.burr_x0020_6_x0020__injec_002

    @property
        def aind_behavior_x0020__fiber_x00(self) -> Optional[Any]:
            """Maps behavior_x0020__fiber_x00 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__fiber_x00 is None
                else {
                    self._nsb.behavior_x0020__fiber_x00.YES: None,
                    self._nsb.behavior_x0020__fiber_x00.NO: None,
                }.get(self._nsb.behavior_x0020__fiber_x00, None)
            )
    
        @property
        def aind_behavior_x0020__first_x00(self) -> Optional[Any]:
            """Maps behavior_x0020__first_x00 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__first_x00 is None
                else {
                    self._nsb.behavior_x0020__first_x00.N_1_1: None,
                    self._nsb.behavior_x0020__first_x00.N_1_2: None,
                    self._nsb.behavior_x0020__first_x00.N_2: None,
                    self._nsb.behavior_x0020__first_x00.N_3: None,
                    self._nsb.behavior_x0020__first_x00.N_4: None,
                    self._nsb.behavior_x0020__first_x00.N_5: None,
                    self._nsb.behavior_x0020__first_x00.N_6: None,
                    self._nsb.behavior_x0020__first_x00.FINAL: None,
                    self._nsb.behavior_x0020__first_x00.GRADUATED: None,
                    self._nsb.behavior_x0020__first_x00.N_A: None,
                }.get(self._nsb.behavior_x0020__first_x00, None)
            )
    
        @property
        def aind_behavior_x0020__first_x00_001(self) -> Optional[Any]:
            """Maps behavior_x0020__first_x00_001 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__first_x00_001 is None
                else {
                    self._nsb.behavior_x0020__first_x00_001.N_1_1: None,
                    self._nsb.behavior_x0020__first_x00_001.N_1_2: None,
                    self._nsb.behavior_x0020__first_x00_001.N_2: None,
                    self._nsb.behavior_x0020__first_x00_001.N_3: None,
                    self._nsb.behavior_x0020__first_x00_001.N_4: None,
                    self._nsb.behavior_x0020__first_x00_001.N_5: None,
                    self._nsb.behavior_x0020__first_x00_001.N_6: None,
                    self._nsb.behavior_x0020__first_x00_001.FINAL: None,
                    self._nsb.behavior_x0020__first_x00_001.GRADUATED: None,
                    self._nsb.behavior_x0020__first_x00_001.N_A: None,
                }.get(self._nsb.behavior_x0020__first_x00_001, None)
            )
    
        @property
        def aind_behavior_x0020__platform(self) -> Optional[Any]:
            """Maps behavior_x0020__platform to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__platform is None
                else {
                    self._nsb.behavior_x0020__platform.MINDSCOPE: None,
                    self._nsb.behavior_x0020__platform.FORAGING: None,
                    self._nsb.behavior_x0020__platform.VR: None,
                }.get(self._nsb.behavior_x0020__platform, None)
            )
    
        @property
        def aind_behavior_x0020__type(self) -> Optional[Any]:
            """Maps behavior_x0020__type to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__type is None
                else {
                    self._nsb.behavior_x0020__type.SELECT: None,
                    self._nsb.behavior_x0020__type.FORAGING: None,
                    self._nsb.behavior_x0020__type.FORAGING_FP: None,
                    self._nsb.behavior_x0020__type.WR__HAB: None,
                    self._nsb.behavior_x0020__type.HAB__ONLY: None,
                }.get(self._nsb.behavior_x0020__type, None)
            )
    
        @property
        def aind_behavior_x0020_fip_x0020(self) -> Optional[Any]:
            """Maps behavior_x0020_fip_x0020 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020_fip_x0020 is None
                else {
                    self._nsb.behavior_x0020_fip_x0020.N_A: None,
                    self._nsb.behavior_x0020_fip_x0020.NORMAL: None,
                    self._nsb.behavior_x0020_fip_x0020.AXON: None,
                }.get(self._nsb.behavior_x0020_fip_x0020, None)
            )
    
        @property
        def aind_black_x0020__cement(self) -> Optional[Any]:
            """Maps black_x0020__cement to aind model."""
            return (
                None
                if self._nsb.black_x0020__cement is None
                else {
                    self._nsb.black_x0020__cement.YES: None,
                    self._nsb.black_x0020__cement.NO: None,
                }.get(self._nsb.black_x0020__cement, None)
            )
    
        @property
        def aind_breg2_lamb(self) -> Optional[str]:
            """Maps breg2_lamb to aind model."""
            return self._nsb.breg2_lamb

    @property
        def aind_burr_x0020_1_x0020__injec_006(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__injec_006 to aind model."""
            return self._nsb.burr_x0020_1_x0020__injec_006

    @property
        def aind_burr_x0020_6_x0020__injec_004(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020__injec_004 to aind model."""
            return self._nsb.burr_x0020_6_x0020__injec_004

    @property
        def aind_burr_x0020_1_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_1_x0020__fiber.STANDARD_PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_1_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_1_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__grid(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__grid to aind model."""
            return self._nsb.burr_x0020_1_x0020__grid

    @property
        def aind_burr_x0020_6_x0020__injec_001(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020__injec_001 to aind model."""
            return self._nsb.burr_x0020_6_x0020__injec_001

    @property
        def aind_lab_tracks_x0020_id1(self) -> Optional[str]:
            """Maps lab_tracks_x0020_id1 to aind model."""
            return self._nsb.lab_tracks_x0020_id1

    @property
        def aind_burr_x0020__hole_x0020_1(self) -> Optional[Any]:
            """Maps burr_x0020__hole_x0020_1 to aind model."""
            return (
                None
                if self._nsb.burr_x0020__hole_x0020_1 is None
                else {
                    self._nsb.burr_x0020__hole_x0020_1.COMPLETE: None,
                }.get(self._nsb.burr_x0020__hole_x0020_1, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_1(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_1 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_1 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_1.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_1.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_1.SPINAL__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_1.N_9__GRID__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_1.N_6__GRID__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_1.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_1.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_1, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_2(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_2 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_2 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_2.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_2.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_2.SPINAL__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_2.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_2.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_2, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_3(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_3 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_3 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_3.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_3.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_3.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_3.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_3, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_4(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_4 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_4 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_4.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_4.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_4.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_4.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_4, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_5(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_5 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_5 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_5.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_5.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_5.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_5.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_5, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_6(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_6 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_6 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_6.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_6.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_6.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_6.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_6, None)
            )
    
        @property
        def aind_care_x0020__moduele(self) -> Optional[Any]:
            """Maps care_x0020__moduele to aind model."""
            return (
                None
                if self._nsb.care_x0020__moduele is None
                else {
                    self._nsb.care_x0020__moduele.SELECT: None,
                    self._nsb.care_x0020__moduele.CM_S_01_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_01_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_03_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_03_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_04_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_04_C_D: None,
                }.get(self._nsb.care_x0020__moduele, None)
            )
    
        @property
        def aind_color_tag(self) -> Optional[str]:
            """Maps color_tag to aind model."""
            return self._nsb.color_tag

    @property
        def aind_burr4_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr4_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr4_x0020__virus_x0020 is None
                else {
                    self._nsb.burr4_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr4_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr4_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr4_x0020_a_x002f_p to aind model."""
            return self._nsb.burr4_x0020_a_x002f_p

    @property
        def aind_burr3_x0020_d_x002f_v(self) -> Optional[str]:
            """Maps burr3_x0020_d_x002f_v to aind model."""
            return self._nsb.burr3_x0020_d_x002f_v

    @property
        def aind_procedure_x0020__family(self) -> Optional[Any]:
            """Maps procedure_x0020__family to aind model."""
            return (
                None
                if self._nsb.procedure_x0020__family is None
                else {
                    self._nsb.procedure_x0020__family.SELECT: None,
                    self._nsb.procedure_x0020__family.INJECTION: None,
                    self._nsb.procedure_x0020__family.FIBER__OPTIC__IMPLANT: None,
                    self._nsb.procedure_x0020__family.CRANIAL__WINDOW: None,
                    self._nsb.procedure_x0020__family.HEADPOST_ONLY: None,
                    self._nsb.procedure_x0020__family.TRAINING: None,
                    self._nsb.procedure_x0020__family.CUSTOM: None,
                    self._nsb.procedure_x0020__family.DEVELOPMENT: None,
                }.get(self._nsb.procedure_x0020__family, None)
            )
    
        @property
        def aind_procedure_x0020__slots(self) -> Optional[Any]:
            """Maps procedure_x0020__slots to aind model."""
            return (
                None
                if self._nsb.procedure_x0020__slots is None
                else {
                    self._nsb.procedure_x0020__slots.SELECT: None,
                    self._nsb.procedure_x0020__slots.SINGLE_SURGICAL_SESSION: None,
                    self._nsb.procedure_x0020__slots.INITIAL_SURGERY_WITH_FOLL: None,
                }.get(self._nsb.procedure_x0020__slots, None)
            )
    
        @property
        def aind_procedure_x0020_t2(self) -> Optional[Any]:
            """Maps procedure_x0020_t2 to aind model."""
            return (
                None
                if self._nsb.procedure_x0020_t2 is None
                else {
                    self._nsb.procedure_x0020_t2.SELECT: None,
                    self._nsb.procedure_x0020_t2.N_2_P: None,
                    self._nsb.procedure_x0020_t2.NP: None,
                    self._nsb.procedure_x0020_t2.N_A: None,
                }.get(self._nsb.procedure_x0020_t2, None)
            )
    
        @property
        def aind_project_id(self) -> Optional[Any]:
            """Maps project_id to aind model."""
            return (
                None
                if self._nsb.project_id is None
                else {
                    self._nsb.project_id.N_101_03_001_10__COSTA_PG: None,
                    self._nsb.project_id.N_102_01_009_10_CTY__MORP: None,
                    self._nsb.project_id.N_102_01_011_10_CTY__CONN: None,
                    self._nsb.project_id.N_102_01_012_10_CTY__CONN: None,
                    self._nsb.project_id.N_102_01_016_10_CTY__TAXO: None,
                    self._nsb.project_id.N_102_01_029_20_CTY_BRAIN: None,
                    self._nsb.project_id.N_102_01_031_20_W4_CTY_EU: None,
                    self._nsb.project_id.N_102_01_031_20_W5_CTY_EU: None,
                    self._nsb.project_id.N_102_01_032_20_CTY__MOUS: None,
                    self._nsb.project_id.N_102_01_036_20_CTY__DISS: None,
                    self._nsb.project_id.N_102_01_040_20_CTY_BRAIN: None,
                    self._nsb.project_id.N_102_01_043_20_CTY__OPTI: None,
                    self._nsb.project_id.N_102_01_044_10_CTY__GENO: None,
                    self._nsb.project_id.N_102_01_045_10_CTY_IVSCC: None,
                    self._nsb.project_id.N_102_01_046_20_CTY__WEIL: None,
                    self._nsb.project_id.N_102_01_048_10_CTY__BARC: None,
                    self._nsb.project_id.N_102_01_049_20_CTY__OPIO: None,
                    self._nsb.project_id.N_102_01_054_20_CTY_PFAC: None,
                    self._nsb.project_id.N_102_01_055_20_CTY_EM__M: None,
                    self._nsb.project_id.N_102_01_059_20_CTY_SCORC: None,
                    self._nsb.project_id.N_102_01_060_20_CTY__BRAI: None,
                    self._nsb.project_id.N_102_01_061_20_CTY_BICAN: None,
                    self._nsb.project_id.N_102_01_062_20_CTY_BICAN: None,
                    self._nsb.project_id.N_102_01_064_10_CTY__GENE: None,
                    self._nsb.project_id.N_102_01_066_20_AIBS_CTY: None,
                    self._nsb.project_id.N_102_01_066_20_AIND_CTY: None,
                    self._nsb.project_id.N_102_01_068_20_CTY_CONNE: None,
                    self._nsb.project_id.N_102_01_069_20__PRE__SPE: None,
                    self._nsb.project_id.N_102_01_070_20_CTY_CONNE: None,
                    self._nsb.project_id.N_102_01_078_20_AIBS__VOC: None,
                    self._nsb.project_id.N_102_01_079_20_AIBS_CONN: None,
                    self._nsb.project_id.N_102_01_999_10_CTY__PROG: None,
                    self._nsb.project_id.N_102_02_004_10_BTV__VISU: None,
                    self._nsb.project_id.N_102_02_012_20_BTV_BRAIN: None,
                    self._nsb.project_id.N_102_04_004_10_OTH__MERI: None,
                    self._nsb.project_id.N_102_04_006_20_OTH__MEAS: None,
                    self._nsb.project_id.N_102_04_007_10_APLD__TAR: None,
                    self._nsb.project_id.N_102_04_010_10_CTY_SR_SL: None,
                    self._nsb.project_id.N_102_04_011_10_CTY_SR_SY: None,
                    self._nsb.project_id.N_102_04_012_10_CTY_SR__F: None,
                    self._nsb.project_id.N_102_04_014_10_CTY__PARK: None,
                    self._nsb.project_id.N_102_04_016_20_CTY__DRAV: None,
                    self._nsb.project_id.N_102_88_001_10_XPG__CORE: None,
                    self._nsb.project_id.N_102_88_003_10__ANIMAL: None,
                    self._nsb.project_id.N_102_88_005_10__TRANSGEN: None,
                    self._nsb.project_id.N_102_88_008_10__LAB__ANI: None,
                    self._nsb.project_id.N_106_01_001_10__IMMUNOLO: None,
                    self._nsb.project_id.N_110_01_001_10_PG__PROTE: None,
                    self._nsb.project_id.N_121_01_016_20_MSP_BRAIN: None,
                    self._nsb.project_id.N_121_01_018_20_MSP__EPHA: None,
                    self._nsb.project_id.N_121_01_023_20_MSP__TEMP: None,
                    self._nsb.project_id.N_121_01_025_20_MSP_U01: None,
                    self._nsb.project_id.N_121_01_026_20_MSP__TEMP: None,
                    self._nsb.project_id.N_122_01_001_10_AIND__SCI: None,
                    self._nsb.project_id.N_122_01_002_20__MOLECULA: None,
                    self._nsb.project_id.N_122_01_002_20__PROJECT: None,
                    self._nsb.project_id.N_122_01_002_20__PROJECT_2: None,
                    self._nsb.project_id.N_122_01_002_20__PROJECT_3: None,
                    self._nsb.project_id.N_122_01_004_20_AIND__BRA: None,
                    self._nsb.project_id.N_122_01_010_20_AIND__POO: None,
                    self._nsb.project_id.N_122_01_011_20_AIND__COH: None,
                    self._nsb.project_id.N_122_01_012_20_AIND_RF1: None,
                    self._nsb.project_id.N_122_01_013_10_MSP__SCIE: None,
                    self._nsb.project_id.N_122_01_014_20_AIND__SIE: None,
                    self._nsb.project_id.N_122_01_019_20_AIND_CZI: None,
                    self._nsb.project_id.N_122_01_020_20_AIBS__COH: None,
                    self._nsb.project_id.N_122_01_020_20_AIND__COH: None,
                    self._nsb.project_id.N_122_01_022_20_AIND__POD: None,
                    self._nsb.project_id.N_123_01_003_20__MOTOR__C: None,
                    self._nsb.project_id.N_124_01_001_10__BRAIN__C: None,
                    self._nsb.project_id.N_125_01_001_10__SEA_HUB: None,
                    self._nsb.project_id.AAV_PRODUCTION_102_88_004: None,
                    self._nsb.project_id.R_D_102_88_004_10: None,
                }.get(self._nsb.project_id, None)
            )
    
        @property
        def aind_protocol(self) -> Optional[Any]:
            """Maps protocol to aind model."""
            return (
                None
                if self._nsb.protocol is None
                else {
                    self._nsb.protocol.SELECT: None,
                    self._nsb.protocol.N_2119__TRAINING_AND_QUAL: None,
                    self._nsb.protocol.N_2201__INTERROGATING_PRO: None,
                    self._nsb.protocol.N_2202__TESTING_AA_VS_IN: None,
                    self._nsb.protocol.N_2204__PRIMARY_NEURON_AN: None,
                    self._nsb.protocol.N_2205__OPTIMIZATION_AND: None,
                    self._nsb.protocol.N_2207__IN__VITRO__BRAIN: None,
                    self._nsb.protocol.N_2212__INVESTIGATING__BR: None,
                    self._nsb.protocol.N_2301__TESTING_OF_ENHANC: None,
                    self._nsb.protocol.N_2304__NEUROSURGERY__BEH: None,
                    self._nsb.protocol.N_2305__IN__VIVO__BRAIN: None,
                    self._nsb.protocol.N_2306__PATCH_SEQ_CHARACT: None,
                    self._nsb.protocol.N_2307__DISSECTING_THE_NE: None,
                    self._nsb.protocol.N_2308__INDUCTION_OF__IMM: None,
                    self._nsb.protocol.N_2401__THE_USE_OF_MICE_F: None,
                    self._nsb.protocol.N_2402__BRAIN__OBSERVATOR: None,
                    self._nsb.protocol.N_2403__ELECTROPHYSIOLOGY: None,
                    self._nsb.protocol.N_2405__ANALYSIS_OF__INTE: None,
                    self._nsb.protocol.N_2406__CHARACTERIZATION: None,
                    self._nsb.protocol.N_2410__VALIDATION_OF_BRA: None,
                    self._nsb.protocol.N_2412__CIRCUIT_TRACING_A: None,
                    self._nsb.protocol.N_2413__NEUROPHYSIOLOGY_O: None,
                    self._nsb.protocol.N_2414__ELECTROPHYSIOLOGI: None,
                    self._nsb.protocol.N_2415__OPTOPHYSIOLOGICAL: None,
                    self._nsb.protocol.N_2416__ANATOMICAL_ANALYS: None,
                    self._nsb.protocol.N_2417__CHARACTERIZATION: None,
                    self._nsb.protocol.N_2418__IN__VITRO__SINGLE: None,
                    self._nsb.protocol.N_2427__OPEN_SCOPE__MINDS: None,
                }.get(self._nsb.protocol, None)
            )
    
        @property
        def aind_ret_setting0(self) -> Optional[Any]:
            """Maps ret_setting0 to aind model."""
            return (
                None
                if self._nsb.ret_setting0 is None
                else {
                    self._nsb.ret_setting0.OFF: None,
                    self._nsb.ret_setting0.ON: None,
                }.get(self._nsb.ret_setting0, None)
            )
    
        @property
        def aind_ret_setting1(self) -> Optional[Any]:
            """Maps ret_setting1 to aind model."""
            return (
                None
                if self._nsb.ret_setting1 is None
                else {
                    self._nsb.ret_setting1.OFF: None,
                    self._nsb.ret_setting1.ON: None,
                }.get(self._nsb.ret_setting1, None)
            )
    
        @property
        def aind_round1_inj_isolevel(self) -> Optional[str]:
            """Maps round1_inj_isolevel to aind model."""
            return self._nsb.round1_inj_isolevel

    @property
        def aind_age_x0020_at_x0020__injec(self) -> Optional[str]:
            """Maps age_x0020_at_x0020__injec to aind model."""
            return self._nsb.age_x0020_at_x0020__injec

    @property
        def aind_fiber_x0020__implant6_x00_001(self) -> Optional[str]:
            """Maps fiber_x0020__implant6_x00_001 to aind model."""
            return self._nsb.fiber_x0020__implant6_x00_001

    @property
        def aind_folder_child_count(self) -> Optional[str]:
            """Maps folder_child_count to aind model."""
            return self._nsb.folder_child_count

    @property
        def aind_burr_x0020_6_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020__angle to aind model."""
            return self._nsb.burr_x0020_6_x0020__angle

    @property
        def aind_craniotomy_x0020__perform(self) -> Optional[Any]:
            """Maps craniotomy_x0020__perform to aind model."""
            return (
                None
                if self._nsb.craniotomy_x0020__perform is None
                else {
                    self._nsb.craniotomy_x0020__perform.INITIAL__SURGERY: None,
                    self._nsb.craniotomy_x0020__perform.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.craniotomy_x0020__perform, None)
            )
    
        @property
        def aind_created(self) -> Optional[str]:
            """Maps created to aind model."""
            return self._nsb.created

    @property
        def aind_weight_x0020_after_x0020(self) -> Optional[str]:
            """Maps weight_x0020_after_x0020 to aind model."""
            return self._nsb.weight_x0020_after_x0020

    @property
        def aind_li_ms_x0020__required(self) -> Optional[Any]:
            """Maps li_ms_x0020__required to aind model."""
            return (
                None
                if self._nsb.li_ms_x0020__required is None
                else {
                    self._nsb.li_ms_x0020__required.SELECT: None,
                    self._nsb.li_ms_x0020__required.LIMS: None,
                    self._nsb.li_ms_x0020__required.SLIMS: None,
                    self._nsb.li_ms_x0020__required.N_A: None,
                }.get(self._nsb.li_ms_x0020__required, None)
            )
    
        @property
        def aind_light_cycle(self) -> Optional[Any]:
            """Maps light_cycle to aind model."""
            return (
                None
                if self._nsb.light_cycle is None
                else {
                    self._nsb.light_cycle.STANDARD__LIGHT__CYCLE_6A: None,
                    self._nsb.light_cycle.REVERSE__LIGHT__CYCLE_9PM: None,
                    self._nsb.light_cycle.N_249_ABSL2: None,
                }.get(self._nsb.light_cycle, None)
            )
    
        @property
        def aind_lims_project(self) -> Optional[Any]:
            """Maps lims_project to aind model."""
            return (
                None
                if self._nsb.lims_project is None
                else {
                    self._nsb.lims_project.N_0200: None,
                    self._nsb.lims_project.N_0309: None,
                    self._nsb.lims_project.N_0310: None,
                    self._nsb.lims_project.N_0311: None,
                    self._nsb.lims_project.N_0312: None,
                    self._nsb.lims_project.N_0314: None,
                    self._nsb.lims_project.N_0316: None,
                    self._nsb.lims_project.N_0319: None,
                    self._nsb.lims_project.N_0320: None,
                    self._nsb.lims_project.N_0321: None,
                    self._nsb.lims_project.N_03212: None,
                    self._nsb.lims_project.N_03213: None,
                    self._nsb.lims_project.N_03214: None,
                    self._nsb.lims_project.N_0322: None,
                    self._nsb.lims_project.N_0324: None,
                    self._nsb.lims_project.N_0325: None,
                    self._nsb.lims_project.N_0326: None,
                    self._nsb.lims_project.N_0327: None,
                    self._nsb.lims_project.N_03272: None,
                    self._nsb.lims_project.N_0328: None,
                    self._nsb.lims_project.N_0329: None,
                    self._nsb.lims_project.N_0331: None,
                    self._nsb.lims_project.N_0334: None,
                    self._nsb.lims_project.N_03342: None,
                    self._nsb.lims_project.N_0335: None,
                    self._nsb.lims_project.N_0336: None,
                    self._nsb.lims_project.N_0338: None,
                    self._nsb.lims_project.N_0339: None,
                    self._nsb.lims_project.N_03392: None,
                    self._nsb.lims_project.N_0340: None,
                    self._nsb.lims_project.N_0342: None,
                    self._nsb.lims_project.N_03422: None,
                    self._nsb.lims_project.N_0343: None,
                    self._nsb.lims_project.N_0344: None,
                    self._nsb.lims_project.N_0345: None,
                    self._nsb.lims_project.N_0346: None,
                    self._nsb.lims_project.N_0350: None,
                    self._nsb.lims_project.N_0350X: None,
                    self._nsb.lims_project.N_0351: None,
                    self._nsb.lims_project.N_0351X: None,
                    self._nsb.lims_project.N_0354: None,
                    self._nsb.lims_project.N_0355: None,
                    self._nsb.lims_project.N_0357: None,
                    self._nsb.lims_project.N_0358: None,
                    self._nsb.lims_project.N_0359: None,
                    self._nsb.lims_project.N_0360: None,
                    self._nsb.lims_project.N_03602: None,
                    self._nsb.lims_project.N_0362: None,
                    self._nsb.lims_project.N_0363: None,
                    self._nsb.lims_project.N_0364: None,
                    self._nsb.lims_project.N_0365: None,
                    self._nsb.lims_project.N_0365X: None,
                    self._nsb.lims_project.N_0366: None,
                    self._nsb.lims_project.N_0366X: None,
                    self._nsb.lims_project.N_0367: None,
                    self._nsb.lims_project.N_0369: None,
                    self._nsb.lims_project.N_0371: None,
                    self._nsb.lims_project.N_0372: None,
                    self._nsb.lims_project.N_0372X: None,
                    self._nsb.lims_project.N_0374: None,
                    self._nsb.lims_project.N_0376: None,
                    self._nsb.lims_project.N_0376A: None,
                    self._nsb.lims_project.N_0376X: None,
                    self._nsb.lims_project.N_0378: None,
                    self._nsb.lims_project.N_0378X: None,
                    self._nsb.lims_project.N_0380: None,
                    self._nsb.lims_project.N_0384: None,
                    self._nsb.lims_project.N_0386: None,
                    self._nsb.lims_project.N_0388: None,
                    self._nsb.lims_project.AIND_MSMA: None,
                    self._nsb.lims_project.AIND_DISCOVERY: None,
                    self._nsb.lims_project.AIND_EPHYS: None,
                    self._nsb.lims_project.AIND_OPHYS: None,
                    self._nsb.lims_project.APR_OX: None,
                    self._nsb.lims_project.A_XL_OX: None,
                    self._nsb.lims_project.BA_RSEQ__GENETIC_TOOLS: None,
                    self._nsb.lims_project.BRAIN_STIM: None,
                    self._nsb.lims_project.BRAINTV_VIRAL_STRATEGIES: None,
                    self._nsb.lims_project.C200: None,
                    self._nsb.lims_project.C600: None,
                    self._nsb.lims_project.C600_LATERAL: None,
                    self._nsb.lims_project.C600X: None,
                    self._nsb.lims_project.CELLTYPES_TRANSGENIC_CHAR: None,
                    self._nsb.lims_project.CITRICACIDPILOT: None,
                    self._nsb.lims_project.CON_9999: None,
                    self._nsb.lims_project.CON_C505: None,
                    self._nsb.lims_project.CON_CS04: None,
                    self._nsb.lims_project.DEEPSCOPE_SLM_DEVELOPMENT: None,
                    self._nsb.lims_project.DYNAMIC_ROUTING_BEHAVIOR: None,
                    self._nsb.lims_project.DYNAMIC_ROUTING_OPTO_DEV: None,
                    self._nsb.lims_project.DYNAMIC_ROUTING_SURGICAL: None,
                    self._nsb.lims_project.DYNAMIC_ROUTING_TASK1_PRO: None,
                    self._nsb.lims_project.DYNAMIC_ROUTING_TASK2_PRO: None,
                    self._nsb.lims_project.DYNAMIC_ROUTING_ULTRA_OPT: None,
                    self._nsb.lims_project.H120: None,
                    self._nsb.lims_project.H200: None,
                    self._nsb.lims_project.H301: None,
                    self._nsb.lims_project.H301T: None,
                    self._nsb.lims_project.H301_X: None,
                    self._nsb.lims_project.H501_X: None,
                    self._nsb.lims_project.H504: None,
                    self._nsb.lims_project.IS_IX: None,
                    self._nsb.lims_project.LARGE_SCALE_VOLTAGE: None,
                    self._nsb.lims_project.LEARNINGM_FISH_DEVELOPMEN: None,
                    self._nsb.lims_project.LEARNINGM_FISH_TASK1_A: None,
                    self._nsb.lims_project.M301T: None,
                    self._nsb.lims_project.MESOSCOPE_DEVELOPMENT: None,
                    self._nsb.lims_project.M_FISH_PLATFORM_DEVELOPME: None,
                    self._nsb.lims_project.MINDSCOPE_TRANSGENIC_CHAR: None,
                    self._nsb.lims_project.M_IVSCC_MET: None,
                    self._nsb.lims_project.M_IVSCC_ME_TX: None,
                    self._nsb.lims_project.M_M_PATCHX: None,
                    self._nsb.lims_project.M_MPATC_HX: None,
                    self._nsb.lims_project.MOUSE_BRAIN_CELL_ATLAS_CH: None,
                    self._nsb.lims_project.MOUSE_BRAIN_CELL_ATLAS_CH_2: None,
                    self._nsb.lims_project.MOUSE_BRAIN_CELL_ATLAS_TR: None,
                    self._nsb.lims_project.MOUSE_FULL_MORPHOLOGY_FMO: None,
                    self._nsb.lims_project.MOUSE_GENETIC_TOOLS_PROJE: None,
                    self._nsb.lims_project.M_VISP_TAXL_O: None,
                    self._nsb.lims_project.MULTISCOPE_SIGNAL_NOISE: None,
                    self._nsb.lims_project.N200: None,
                    self._nsb.lims_project.N310: None,
                    self._nsb.lims_project.NEUROPIXEL_VISUAL_BEHAVIO: None,
                    self._nsb.lims_project.NEUROPIXEL_VISUAL_BEHAVIO_2: None,
                    self._nsb.lims_project.NEUROPIXEL_VISUAL_CODING: None,
                    self._nsb.lims_project.OLVSX: None,
                    self._nsb.lims_project.OM_FIS_HCOREGISTRATIONPIL: None,
                    self._nsb.lims_project.OM_FISH_CUX2_MESO: None,
                    self._nsb.lims_project.OM_FISH_GAD2_MESO: None,
                    self._nsb.lims_project.OM_FISH_GAD2_PILOT: None,
                    self._nsb.lims_project.OM_FISH_RBP4_MESO: None,
                    self._nsb.lims_project.OM_FISH_RORB_PILOT: None,
                    self._nsb.lims_project.OM_FISHRO_BINJECTIONVIRUS: None,
                    self._nsb.lims_project.OM_FISH_SST_MESO: None,
                    self._nsb.lims_project.OM_FISH_VIP_MESO: None,
                    self._nsb.lims_project.OPEN_SCOPE_DENDRITE_COUPL: None,
                    self._nsb.lims_project.OPENSCOPE_DEVELOPMENT: None,
                    self._nsb.lims_project.OPEN_SCOPE_ILLUSION: None,
                    self._nsb.lims_project.OPEN_SCOPE_GLOBAL_LOCAL_O: None,
                    self._nsb.lims_project.OPENSCOPE_GAMMA_PILOT: None,
                    self._nsb.lims_project.OPENSCOPE_GAMMA_PRODUCTLO: None,
                    self._nsb.lims_project.OPENSCOPELNJECTION_PILOT: None,
                    self._nsb.lims_project.OPEN_SCOPE_LOOP: None,
                    self._nsb.lims_project.OPENSCOPE_MOTION_PLLOT: None,
                    self._nsb.lims_project.OPENSCOPE_MOTION_PRODUCTI: None,
                    self._nsb.lims_project.OPENSCOPE_MULTIPLEX_PILOT: None,
                    self._nsb.lims_project.OPENSCOPE_MULTIPLEX_PRODU: None,
                    self._nsb.lims_project.OPEN_SCOPE_PSYCODE: None,
                    self._nsb.lims_project.OPEN_SCOPE_SEQUENCE_LEARN: None,
                    self._nsb.lims_project.OPEN_SCOPE_TEMPORAL_BARCO: None,
                    self._nsb.lims_project.OPEN_SCOPE_TEXTURE: None,
                    self._nsb.lims_project.OPEN_SCOPE_VISION2_HIPPOC: None,
                    self._nsb.lims_project.OPEN_SCOPE_VISMO: None,
                    self._nsb.lims_project.OPH5_X: None,
                    self._nsb.lims_project.SLC6_A1_NEUROPIXEL: None,
                    self._nsb.lims_project.SMART_SPIM__GENETIC_TOOLS: None,
                    self._nsb.lims_project.SURGERY_X: None,
                    self._nsb.lims_project.T301: None,
                    self._nsb.lims_project.T301T: None,
                    self._nsb.lims_project.T301_X: None,
                    self._nsb.lims_project.T503: None,
                    self._nsb.lims_project.T503_X: None,
                    self._nsb.lims_project.T504: None,
                    self._nsb.lims_project.T504_X: None,
                    self._nsb.lims_project.T600: None,
                    self._nsb.lims_project.T601: None,
                    self._nsb.lims_project.T601_X: None,
                    self._nsb.lims_project.TCYTX: None,
                    self._nsb.lims_project.TASK_TRAINED_NETWORKS_MUL: None,
                    self._nsb.lims_project.TASK_TRAINED_NETWORKS_NEU: None,
                    self._nsb.lims_project.TEMPLETON_PSYCHEDELICS: None,
                    self._nsb.lims_project.TEMPLETON_TTOC: None,
                    self._nsb.lims_project.TINY_BLUE_DOT_BEHAVIOR: None,
                    self._nsb.lims_project.U01_BFCT: None,
                    self._nsb.lims_project.VARIABILITY_AIM1: None,
                    self._nsb.lims_project.VARIABILITY_AIM1_PILOT: None,
                    self._nsb.lims_project.VARIABILITY_SPONTANEOUS: None,
                    self._nsb.lims_project.VI_DEEP_DIVE_EM_VOLUME: None,
                    self._nsb.lims_project.VI_DEEPDLVE_DEEPSCOPE_PIE: None,
                    self._nsb.lims_project.VIP_AXONAL_V1_PHASE1: None,
                    self._nsb.lims_project.VIP_SOMATIC_V1_MESO: None,
                    self._nsb.lims_project.VIP_SOMATIC_V1_PHASE1: None,
                    self._nsb.lims_project.VIP_SOMATIC_V1_PHASE2: None,
                    self._nsb.lims_project.VISUAL_BEHAVIOR: None,
                    self._nsb.lims_project.VISUAL_BEHAVIOR_DEVELOPME: None,
                    self._nsb.lims_project.VISUAL_BEHAVIOR_MULTISCOP: None,
                    self._nsb.lims_project.VISUAL_BEHAVIOR_MULTISCOP_2: None,
                    self._nsb.lims_project.VISUAL_BEHAV_IOR_MULTISCO: None,
                    self._nsb.lims_project.VISUAL_BEHAVIOR_TASK1_B: None,
                }.get(self._nsb.lims_project, None)
            )
    
        @property
        def aind_lims_taskflow(self) -> Optional[Any]:
            """Maps lims_taskflow to aind model."""
            return (
                None
                if self._nsb.lims_taskflow is None
                else {
                    self._nsb.lims_taskflow.AIND__EPHYS__SURGERY_ONLY: None,
                    self._nsb.lims_taskflow.AIND__EPHYS__PASSIVE__BEH: None,
                    self._nsb.lims_taskflow.AIND_U19_AAV__RETROGRADE: None,
                    self._nsb.lims_taskflow.AIND_U19__RAB_V__RETROGRA: None,
                    self._nsb.lims_taskflow.AIND_U19__THALAMUS: None,
                    self._nsb.lims_taskflow.AIND__WATERLOG: None,
                    self._nsb.lims_taskflow.BRAIN__LARGE__SCALE__RECO: None,
                    self._nsb.lims_taskflow.BRAIN__MOUSE__BRAIN__CELL: None,
                    self._nsb.lims_taskflow.BRAIN__OBSERVATORY__DEEPS: None,
                    self._nsb.lims_taskflow.BRAIN__OBSERVATORY__EPHYS: None,
                    self._nsb.lims_taskflow.BRAIN__OBSERVATORY__MAPSC: None,
                    self._nsb.lims_taskflow.BRAIN__OBSERVATORY__MESOS: None,
                    self._nsb.lims_taskflow.BRAIN__OBSERVATORY__MESOS_2: None,
                    self._nsb.lims_taskflow.BRAIN__OBSERVATORY__NEURO: None,
                    self._nsb.lims_taskflow.BRAIN__OBSERVATORY__TRANS: None,
                    self._nsb.lims_taskflow.BRAIN__OBSERVATORY_V1_DD: None,
                    self._nsb.lims_taskflow.BRAIN__OBSERVATORY__VISUA: None,
                    self._nsb.lims_taskflow.BRAIN__OBSERVATORY__VISUA_2: None,
                    self._nsb.lims_taskflow.BRAIN__OBSERVATORY__VISUA_3: None,
                    self._nsb.lims_taskflow.BRAIN__OBSERVATORY__VISUA_4: None,
                    self._nsb.lims_taskflow.BTV_BRAIN__VIRAL__STRATEG: None,
                    self._nsb.lims_taskflow.CITRIC__ACID__PILOT: None,
                    self._nsb.lims_taskflow.EPHYS__DEV__VISUAL__BEHAV: None,
                    self._nsb.lims_taskflow.EPHYS__DEV__VISUAL__BEHAV_2: None,
                    self._nsb.lims_taskflow.EPHYS__TASK__DEV__DYNAMIC: None,
                    self._nsb.lims_taskflow.EPHYS__TASK__DEV__DYANMIC: None,
                    self._nsb.lims_taskflow.EPHYS__TASK__DEV__DYNAMIC_2: None,
                    self._nsb.lims_taskflow.IVSCC_HVA__RETRO__PATCH_S: None,
                    self._nsb.lims_taskflow.IVSC_CM_INJECTION: None,
                    self._nsb.lims_taskflow.IVSP_CM__INJECTION: None,
                    self._nsb.lims_taskflow.MGT__LAB: None,
                    self._nsb.lims_taskflow.MGT__TISSUE_CYTE: None,
                    self._nsb.lims_taskflow.MINDSCOPE_2_P__TESTING: None,
                    self._nsb.lims_taskflow.MSP__DYNAMIC__ROUTING__BE: None,
                    self._nsb.lims_taskflow.MSP__DYNAMIC__ROUTING__OP: None,
                    self._nsb.lims_taskflow.MSP__DYNAMIC__ROUTING__SU: None,
                    self._nsb.lims_taskflow.MSP__DYNAMIC__ROUTING__UL: None,
                    self._nsb.lims_taskflow.MSP__DYNAMIC__ROUTING__TA: None,
                    self._nsb.lims_taskflow.MSP__DYNAMIC__ROUTING__TA_2: None,
                    self._nsb.lims_taskflow.MSP_G_CA_MP8__TESTING: None,
                    self._nsb.lims_taskflow.MSP_G_CA_MP8__TESTING_RO: None,
                    self._nsb.lims_taskflow.MSP__LEARNING_M_FISH__DEV: None,
                    self._nsb.lims_taskflow.MSP__LEARNING_M_FISH__DEV_2: None,
                    self._nsb.lims_taskflow.MSP__LEARNING_M_FISH__FRO: None,
                    self._nsb.lims_taskflow.MSP__LEARNING_M_FISH__VIR: None,
                    self._nsb.lims_taskflow.MSP_OM_FISH__CO_REGISTRAT: None,
                    self._nsb.lims_taskflow.MSP_OM_FISH__CUX2__PILOT: None,
                    self._nsb.lims_taskflow.MSP_OM_FISH__GAD2__MESO: None,
                    self._nsb.lims_taskflow.MSP_OM_FISH__GAD2__PILOT: None,
                    self._nsb.lims_taskflow.MSP_OM_FISH__RBP4__MESO: None,
                    self._nsb.lims_taskflow.MSP_OM_FISH__RORB__PILOT: None,
                    self._nsb.lims_taskflow.MSP_OM_FISH_ROB__INJECTIO: None,
                    self._nsb.lims_taskflow.MSP_OM_FISH__SST__MESO__G: None,
                    self._nsb.lims_taskflow.MSP_OM_FISH__VIP__MESO__G: None,
                    self._nsb.lims_taskflow.MSP__OPEN_SCOPE__DENDRITE: None,
                    self._nsb.lims_taskflow.MSP__OPEN_SCOPE__ILLUSION: None,
                    self._nsb.lims_taskflow.MSP__OPEN_SCOPE__GLOBAL: None,
                    self._nsb.lims_taskflow.MSP__OPEN_SCOPE__GLOBAL_2: None,
                    self._nsb.lims_taskflow.MSP__TASK__TRAINED__NETWO: None,
                    self._nsb.lims_taskflow.MSP__TASK__TRAINED__NETWO_2: None,
                    self._nsb.lims_taskflow.MSP_U01__BRIDGING__FUNCTI: None,
                    self._nsb.lims_taskflow.MSP__VARIABILITY__AIM_1: None,
                    self._nsb.lims_taskflow.MSP__VARIABILITY__AIM_1_2: None,
                    self._nsb.lims_taskflow.MSP__VARIABILITY__SPONTAN: None,
                    self._nsb.lims_taskflow.MSP_VIP__AXONAL_V1: None,
                    self._nsb.lims_taskflow.MSP_VIP__SOMATIC_V1: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__GAMMA__PILOT: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__GAMMA__PRODUC: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE_LNJECTION__VOL: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__MOTION__PILOT: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__MULTIPLEX__PI: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__MULTIPLEX__PI_2: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__MULTIPLEX__PR: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__MULTLPLEX__PR: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__LOOP: None,
                    self._nsb.lims_taskflow.OPENSCOPE__MOTION__PRODUC: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__PSYCODE: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__SEQUENCE__LEA: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__TEMPORAL__BAR: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__TEMPORAL__BAR_2: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__TEXTURE__ACTI: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__TEXTURE__PASS: None,
                    self._nsb.lims_taskflow.OPENSCOPE__VIRUS__VALIDAT: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__VISION_2__HIP: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE__VISMO: None,
                    self._nsb.lims_taskflow.OPEN_SCOPE_WHC_2_P__DEV: None,
                    self._nsb.lims_taskflow.TEMPLETON_PSYCHEDELICS: None,
                    self._nsb.lims_taskflow.TILTY__MOUSE: None,
                    self._nsb.lims_taskflow.TINY__BLUE__DOT__BEHAVIOR: None,
                    self._nsb.lims_taskflow.TRANSGENIC__CHARACTERIZAT: None,
                    self._nsb.lims_taskflow.VIS_B__DEV__CONTROL__GROU: None,
                    self._nsb.lims_taskflow.VIS_B__LATERAL__PREP__DEV: None,
                    self._nsb.lims_taskflow.VIS_B__TASK_2__DEVELOPMEN: None,
                    self._nsb.lims_taskflow.VGT__ENHANCERS__TRANSSYNA: None,
                }.get(self._nsb.lims_taskflow, None)
            )
    
        @property
        def aind_link_title(self) -> Optional[str]:
            """Maps link_title to aind model."""
            return self._nsb.link_title

    @property
        def aind_burr_x0020_1_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_1_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_1_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_1_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_1_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_2_x0020__fiber.STANDARD__PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_2_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_2_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020__injec to aind model."""
            return self._nsb.burr_x0020_2_x0020__injec

    @property
        def aind_burr3_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr3_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__virus_x0020 is None
                else {
                    self._nsb.burr3_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr3_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr3_x0020_a_x002f_p to aind model."""
            return self._nsb.burr3_x0020_a_x002f_p

    @property
        def aind_burr_x0020_5_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_5_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_5_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_5_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_5_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020_m_x002(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020_m_x002 to aind model."""
            return self._nsb.burr_x0020_5_x0020_m_x002

    @property
        def aind_burr_x0020_2_x0020_intend(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020_intend to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020_intend is None
                else {
                    self._nsb.burr_x0020_2_x0020_intend.N_A: None,
                    self._nsb.burr_x0020_2_x0020_intend.DOPAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend.SEROTONIN: None,
                    self._nsb.burr_x0020_2_x0020_intend.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_2_x0020_intend.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_2_x0020_intend.HISTAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend.GLUTAMATE: None,
                    self._nsb.burr_x0020_2_x0020_intend.GABA: None,
                    self._nsb.burr_x0020_2_x0020_intend.CALCIUM: None,
                    self._nsb.burr_x0020_2_x0020_intend.VOLTAGE: None,
                    self._nsb.burr_x0020_2_x0020_intend.CONTROL: None,
                }.get(self._nsb.burr_x0020_2_x0020_intend, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020_intend_001(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020_intend_001 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020_intend_001 is None
                else {
                    self._nsb.burr_x0020_2_x0020_intend_001.N_A: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.DOPAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.SEROTONIN: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.HISTAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.GLUTAMATE: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.GABA: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.CALCIUM: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.VOLTAGE: None,
                    self._nsb.burr_x0020_2_x0020_intend_001.CONTROL: None,
                }.get(self._nsb.burr_x0020_2_x0020_intend_001, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_2_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_2_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_2_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_2_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_2_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_3_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__angle to aind model."""
            return self._nsb.burr_x0020_3_x0020__angle

    @property
        def aind_burr3_x0020_m_x002f_l(self) -> Optional[str]:
            """Maps burr3_x0020_m_x002f_l to aind model."""
            return self._nsb.burr3_x0020_m_x002f_l

    @property
        def aind_burr_x0020_3_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_3_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_3_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_3_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_3_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_3_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_3_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_3_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_3_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_3_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_4_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__angle to aind model."""
            return self._nsb.burr_x0020_4_x0020__angle

    @property
        def aind_burr_x0020_6_x0020_d_x002_002(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020_d_x002_002 to aind model."""
            return self._nsb.burr_x0020_6_x0020_d_x002_002

    @property
        def aind_burr_x0020_1_x0020__injec_003(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__injec_003 to aind model."""
            return self._nsb.burr_x0020_1_x0020__injec_003

    @property
        def aind_burr2_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr2_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__perform_x002 is None
                else {
                    self._nsb.burr2_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr2_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr2_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr2_x0020__status(self) -> Optional[Any]:
            """Maps burr2_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__status is None
                else {
                    self._nsb.burr2_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr2_x0020__status, None)
            )
    
        @property
        def aind_burr2_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr2_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__virus_x0020 is None
                else {
                    self._nsb.burr2_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr2_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr3_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__injection_x0 is None
                else {
                    self._nsb.burr3_x0020__injection_x0.SELECT: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr3_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr3_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr3_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__perform_x002 is None
                else {
                    self._nsb.burr3_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr3_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr3_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr3_x0020__status(self) -> Optional[Any]:
            """Maps burr3_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__status is None
                else {
                    self._nsb.burr3_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr3_x0020__status, None)
            )
    
        @property
        def aind_burr3_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr3_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__virus_x0020 is None
                else {
                    self._nsb.burr3_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr3_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr3_x0020_a_x002f_p to aind model."""
            return self._nsb.burr3_x0020_a_x002f_p

    @property
        def aind_burr_x0020_1_x0020_intend(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020_intend to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020_intend is None
                else {
                    self._nsb.burr_x0020_1_x0020_intend.N_A: None,
                    self._nsb.burr_x0020_1_x0020_intend.DOPAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend.SEROTONIN: None,
                    self._nsb.burr_x0020_1_x0020_intend.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_1_x0020_intend.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_1_x0020_intend.HISTAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend.GLUTAMATE: None,
                    self._nsb.burr_x0020_1_x0020_intend.GABA: None,
                    self._nsb.burr_x0020_1_x0020_intend.CALCIUM: None,
                    self._nsb.burr_x0020_1_x0020_intend.VOLTAGE: None,
                    self._nsb.burr_x0020_1_x0020_intend.CONTROL: None,
                }.get(self._nsb.burr_x0020_1_x0020_intend, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020_intend_001(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020_intend_001 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020_intend_001 is None
                else {
                    self._nsb.burr_x0020_1_x0020_intend_001.N_A: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.DOPAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.SEROTONIN: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.HISTAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.GLUTAMATE: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.GABA: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.CALCIUM: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.VOLTAGE: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.CONTROL: None,
                }.get(self._nsb.burr_x0020_1_x0020_intend_001, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_1_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_1_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_1_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_1_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_2_x0020__fiber.STANDARD__PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_2_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_2_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020__injec to aind model."""
            return self._nsb.burr_x0020_2_x0020__injec

    @property
        def aind_burr2_x0020__status(self) -> Optional[Any]:
            """Maps burr2_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__status is None
                else {
                    self._nsb.burr2_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr2_x0020__status, None)
            )
    
        @property
        def aind_burr2_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr2_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__virus_x0020 is None
                else {
                    self._nsb.burr2_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr2_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr3_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__injection_x0 is None
                else {
                    self._nsb.burr3_x0020__injection_x0.SELECT: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr3_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr3_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr3_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__perform_x002 is None
                else {
                    self._nsb.burr3_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr3_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr3_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr3_x0020__status(self) -> Optional[Any]:
            """Maps burr3_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__status is None
                else {
                    self._nsb.burr3_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr3_x0020__status, None)
            )
    
        @property
        def aind_burr3_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr3_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__virus_x0020 is None
                else {
                    self._nsb.burr3_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr3_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr3_x0020_a_x002f_p to aind model."""
            return self._nsb.burr3_x0020_a_x002f_p

    @property
        def aind_non_x002d_nsb_x0020__surg(self) -> Optional[bool]:
            """Maps non_x002d_nsb_x0020__surg to aind model."""
            return self._nsb.non_x002d_nsb_x0020__surg

    @property
        def aind_attachments(self) -> Optional[str]:
            """Maps attachments to aind model."""
            return self._nsb.attachments

    @property
        def aind_burr_x0020_hole_x0020_1(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_1 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_1 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_1.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_1.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_1.SPINAL__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_1.N_9__GRID__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_1.N_6__GRID__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_1.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_1.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_1, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_2(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_2 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_2 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_2.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_2.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_2.SPINAL__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_2.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_2.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_2, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_3(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_3 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_3 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_3.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_3.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_3.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_3.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_3, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_4(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_4 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_4 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_4.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_4.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_4.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_4.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_4, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_5(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_5 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_5 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_5.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_5.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_5.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_5.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_5, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_6(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_6 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_6 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_6.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_6.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_6.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_6.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_6, None)
            )
    
        @property
        def aind_care_x0020__moduele(self) -> Optional[Any]:
            """Maps care_x0020__moduele to aind model."""
            return (
                None
                if self._nsb.care_x0020__moduele is None
                else {
                    self._nsb.care_x0020__moduele.SELECT: None,
                    self._nsb.care_x0020__moduele.CM_S_01_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_01_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_03_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_03_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_04_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_04_C_D: None,
                }.get(self._nsb.care_x0020__moduele, None)
            )
    
        @property
        def aind_color_tag(self) -> Optional[str]:
            """Maps color_tag to aind model."""
            return self._nsb.color_tag

    @property
        def aind_procedure_x0020_t2(self) -> Optional[Any]:
            """Maps procedure_x0020_t2 to aind model."""
            return (
                None
                if self._nsb.procedure_x0020_t2 is None
                else {
                    self._nsb.procedure_x0020_t2.SELECT: None,
                    self._nsb.procedure_x0020_t2.N_2_P: None,
                    self._nsb.procedure_x0020_t2.NP: None,
                    self._nsb.procedure_x0020_t2.N_A: None,
                }.get(self._nsb.procedure_x0020_t2, None)
            )
    
        @property
        def aind_project_id(self) -> Optional[Any]:
            """Maps project_id to aind model."""
            return (
                None
                if self._nsb.project_id is None
                else {
                    self._nsb.project_id.N_101_03_001_10__COSTA_PG: None,
                    self._nsb.project_id.N_102_01_009_10_CTY__MORP: None,
                    self._nsb.project_id.N_102_01_011_10_CTY__CONN: None,
                    self._nsb.project_id.N_102_01_012_10_CTY__CONN: None,
                    self._nsb.project_id.N_102_01_016_10_CTY__TAXO: None,
                    self._nsb.project_id.N_102_01_029_20_CTY_BRAIN: None,
                    self._nsb.project_id.N_102_01_031_20_W4_CTY_EU: None,
                    self._nsb.project_id.N_102_01_031_20_W5_CTY_EU: None,
                    self._nsb.project_id.N_102_01_032_20_CTY__MOUS: None,
                    self._nsb.project_id.N_102_01_036_20_CTY__DISS: None,
                    self._nsb.project_id.N_102_01_040_20_CTY_BRAIN: None,
                    self._nsb.project_id.N_102_01_043_20_CTY__OPTI: None,
                    self._nsb.project_id.N_102_01_044_10_CTY__GENO: None,
                    self._nsb.project_id.N_102_01_045_10_CTY_IVSCC: None,
                    self._nsb.project_id.N_102_01_046_20_CTY__WEIL: None,
                    self._nsb.project_id.N_102_01_048_10_CTY__BARC: None,
                    self._nsb.project_id.N_102_01_049_20_CTY__OPIO: None,
                    self._nsb.project_id.N_102_01_054_20_CTY_PFAC: None,
                    self._nsb.project_id.N_102_01_055_20_CTY_EM__M: None,
                    self._nsb.project_id.N_102_01_059_20_CTY_SCORC: None,
                    self._nsb.project_id.N_102_01_060_20_CTY__BRAI: None,
                    self._nsb.project_id.N_102_01_061_20_CTY_BICAN: None,
                    self._nsb.project_id.N_102_01_062_20_CTY_BICAN: None,
                    self._nsb.project_id.N_102_01_064_10_CTY__GENE: None,
                    self._nsb.project_id.N_102_01_066_20_AIBS_CTY: None,
                    self._nsb.project_id.N_102_01_066_20_AIND_CTY: None,
                    self._nsb.project_id.N_102_01_068_20_CTY_CONNE: None,
                    self._nsb.project_id.N_102_01_069_20__PRE__SPE: None,
                    self._nsb.project_id.N_102_01_070_20_CTY_CONNE: None,
                    self._nsb.project_id.N_102_01_078_20_AIBS__VOC: None,
                    self._nsb.project_id.N_102_01_079_20_AIBS_CONN: None,
                    self._nsb.project_id.N_102_01_999_10_CTY__PROG: None,
                    self._nsb.project_id.N_102_02_004_10_BTV__VISU: None,
                    self._nsb.project_id.N_102_02_012_20_BTV_BRAIN: None,
                    self._nsb.project_id.N_102_04_004_10_OTH__MERI: None,
                    self._nsb.project_id.N_102_04_006_20_OTH__MEAS: None,
                    self._nsb.project_id.N_102_04_007_10_APLD__TAR: None,
                    self._nsb.project_id.N_102_04_010_10_CTY_SR_SL: None,
                    self._nsb.project_id.N_102_04_011_10_CTY_SR_SY: None,
                    self._nsb.project_id.N_102_04_012_10_CTY_SR__F: None,
                    self._nsb.project_id.N_102_04_014_10_CTY__PARK: None,
                    self._nsb.project_id.N_102_04_016_20_CTY__DRAV: None,
                    self._nsb.project_id.N_102_88_001_10_XPG__CORE: None,
                    self._nsb.project_id.N_102_88_003_10__ANIMAL: None,
                    self._nsb.project_id.N_102_88_005_10__TRANSGEN: None,
                    self._nsb.project_id.N_102_88_008_10__LAB__ANI: None,
                    self._nsb.project_id.N_106_01_001_10__IMMUNOLO: None,
                    self._nsb.project_id.N_110_01_001_10_PG__PROTE: None,
                    self._nsb.project_id.N_121_01_016_20_MSP_BRAIN: None,
                    self._nsb.project_id.N_121_01_018_20_MSP__EPHA: None,
                    self._nsb.project_id.N_121_01_023_20_MSP__TEMP: None,
                    self._nsb.project_id.N_121_01_025_20_MSP_U01: None,
                    self._nsb.project_id.N_121_01_026_20_MSP__TEMP: None,
                    self._nsb.project_id.N_122_01_001_10_AIND__SCI: None,
                    self._nsb.project_id.N_122_01_002_20__MOLECULA: None,
                    self._nsb.project_id.N_122_01_002_20__PROJECT: None,
                    self._nsb.project_id.N_122_01_002_20__PROJECT_2: None,
                    self._nsb.project_id.N_122_01_002_20__PROJECT_3: None,
                    self._nsb.project_id.N_122_01_004_20_AIND__BRA: None,
                    self._nsb.project_id.N_122_01_010_20_AIND__POO: None,
                    self._nsb.project_id.N_122_01_011_20_AIND__COH: None,
                    self._nsb.project_id.N_122_01_012_20_AIND_RF1: None,
                    self._nsb.project_id.N_122_01_013_10_MSP__SCIE: None,
                    self._nsb.project_id.N_122_01_014_20_AIND__SIE: None,
                    self._nsb.project_id.N_122_01_019_20_AIND_CZI: None,
                    self._nsb.project_id.N_122_01_020_20_AIBS__COH: None,
                    self._nsb.project_id.N_122_01_020_20_AIND__COH: None,
                    self._nsb.project_id.N_122_01_022_20_AIND__POD: None,
                    self._nsb.project_id.N_123_01_003_20__MOTOR__C: None,
                    self._nsb.project_id.N_124_01_001_10__BRAIN__C: None,
                    self._nsb.project_id.N_125_01_001_10__SEA_HUB: None,
                    self._nsb.project_id.AAV_PRODUCTION_102_88_004: None,
                    self._nsb.project_id.R_D_102_88_004_10: None,
                }.get(self._nsb.project_id, None)
            )
    
        @property
        def aind_protocol(self) -> Optional[Any]:
            """Maps protocol to aind model."""
            return (
                None
                if self._nsb.protocol is None
                else {
                    self._nsb.protocol.SELECT: None,
                    self._nsb.protocol.N_2119__TRAINING_AND_QUAL: None,
                    self._nsb.protocol.N_2201__INTERROGATING_PRO: None,
                    self._nsb.protocol.N_2202__TESTING_AA_VS_IN: None,
                    self._nsb.protocol.N_2204__PRIMARY_NEURON_AN: None,
                    self._nsb.protocol.N_2205__OPTIMIZATION_AND: None,
                    self._nsb.protocol.N_2207__IN__VITRO__BRAIN: None,
                    self._nsb.protocol.N_2212__INVESTIGATING__BR: None,
                    self._nsb.protocol.N_2301__TESTING_OF_ENHANC: None,
                    self._nsb.protocol.N_2304__NEUROSURGERY__BEH: None,
                    self._nsb.protocol.N_2305__IN__VIVO__BRAIN: None,
                    self._nsb.protocol.N_2306__PATCH_SEQ_CHARACT: None,
                    self._nsb.protocol.N_2307__DISSECTING_THE_NE: None,
                    self._nsb.protocol.N_2308__INDUCTION_OF__IMM: None,
                    self._nsb.protocol.N_2401__THE_USE_OF_MICE_F: None,
                    self._nsb.protocol.N_2402__BRAIN__OBSERVATOR: None,
                    self._nsb.protocol.N_2403__ELECTROPHYSIOLOGY: None,
                    self._nsb.protocol.N_2405__ANALYSIS_OF__INTE: None,
                    self._nsb.protocol.N_2406__CHARACTERIZATION: None,
                    self._nsb.protocol.N_2410__VALIDATION_OF_BRA: None,
                    self._nsb.protocol.N_2412__CIRCUIT_TRACING_A: None,
                    self._nsb.protocol.N_2413__NEUROPHYSIOLOGY_O: None,
                    self._nsb.protocol.N_2414__ELECTROPHYSIOLOGI: None,
                    self._nsb.protocol.N_2415__OPTOPHYSIOLOGICAL: None,
                    self._nsb.protocol.N_2416__ANATOMICAL_ANALYS: None,
                    self._nsb.protocol.N_2417__CHARACTERIZATION: None,
                    self._nsb.protocol.N_2418__IN__VITRO__SINGLE: None,
                    self._nsb.protocol.N_2427__OPEN_SCOPE__MINDS: None,
                }.get(self._nsb.protocol, None)
            )
    
        @property
        def aind_ret_setting0(self) -> Optional[Any]:
            """Maps ret_setting0 to aind model."""
            return (
                None
                if self._nsb.ret_setting0 is None
                else {
                    self._nsb.ret_setting0.OFF: None,
                    self._nsb.ret_setting0.ON: None,
                }.get(self._nsb.ret_setting0, None)
            )
    
        @property
        def aind_ret_setting1(self) -> Optional[Any]:
            """Maps ret_setting1 to aind model."""
            return (
                None
                if self._nsb.ret_setting1 is None
                else {
                    self._nsb.ret_setting1.OFF: None,
                    self._nsb.ret_setting1.ON: None,
                }.get(self._nsb.ret_setting1, None)
            )
    
        @property
        def aind_round1_inj_isolevel(self) -> Optional[str]:
            """Maps round1_inj_isolevel to aind model."""
            return self._nsb.round1_inj_isolevel

    @property
        def aind_burr_x0020_6_x0020__injec_007(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020__injec_007 to aind model."""
            return self._nsb.burr_x0020_6_x0020__injec_007

    @property
        def aind_fiber_x0020__implant2_x00(self) -> Optional[Any]:
            """Maps fiber_x0020__implant2_x00 to aind model."""
            return (
                None
                if self._nsb.fiber_x0020__implant2_x00 is None
                else {
                    self._nsb.fiber_x0020__implant2_x00.SELECT: None,
                    self._nsb.fiber_x0020__implant2_x00.N_1_0_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_1_5_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_2_0_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_2_5_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_3_0_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_3_5_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_4_0_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_4_5_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_5_0_MM: None,
                }.get(self._nsb.fiber_x0020__implant2_x00, None)
            )
    
        @property
        def aind_fiber_x0020__implant3_x00(self) -> Optional[Any]:
            """Maps fiber_x0020__implant3_x00 to aind model."""
            return (
                None
                if self._nsb.fiber_x0020__implant3_x00 is None
                else {
                    self._nsb.fiber_x0020__implant3_x00.SELECT: None,
                    self._nsb.fiber_x0020__implant3_x00.N_1_0_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_1_5_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_2_0_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_2_5_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_3_0_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_3_5_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_4_0_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_4_5_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_5_0_MM: None,
                }.get(self._nsb.fiber_x0020__implant3_x00, None)
            )
    
        @property
        def aind_fiber_x0020__implant3_x00_001(self) -> Optional[str]:
            """Maps fiber_x0020__implant3_x00_001 to aind model."""
            return self._nsb.fiber_x0020__implant3_x00_001

    @property
        def aind_doc_icon(self) -> Optional[str]:
            """Maps doc_icon to aind model."""
            return self._nsb.doc_icon

    @property
        def aind_burr_x0020_3_x0020_d_x002_001(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020_d_x002_001 to aind model."""
            return self._nsb.burr_x0020_3_x0020_d_x002_001

    @property
        def aind_burr_x0020_5_x0020_d_x002_001(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020_d_x002_001 to aind model."""
            return self._nsb.burr_x0020_5_x0020_d_x002_001

    @property
        def aind_burr6_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr6_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__injection_x0 is None
                else {
                    self._nsb.burr6_x0020__injection_x0.SELECT: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr6_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr6_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr6_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__perform_x002 is None
                else {
                    self._nsb.burr6_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr6_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr6_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr6_x0020__status(self) -> Optional[Any]:
            """Maps burr6_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__status is None
                else {
                    self._nsb.burr6_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr6_x0020__status, None)
            )
    
        @property
        def aind_burr6_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr6_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__virus_x0020 is None
                else {
                    self._nsb.burr6_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr6_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_1_x0020__fiber.STANDARD_PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_1_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_1_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__grid(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__grid to aind model."""
            return self._nsb.burr_x0020_1_x0020__grid

    @property
        def aind_test1(self) -> Optional[str]:
            """Maps test1 to aind model."""
            return self._nsb.test1

    @property
        def aind_burr_x0020_1_x0020__injec_004(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__injec_004 to aind model."""
            return self._nsb.burr_x0020_1_x0020__injec_004

    @property
        def aind_aind_x0020__project_x0020(self) -> Optional[Any]:
            """Maps aind_x0020__project_x0020 to aind model."""
            return (
                None
                if self._nsb.aind_x0020__project_x0020 is None
                else {
                    self._nsb.aind_x0020__project_x0020.BRAIN__WIDE__CIRCUIT__DYN: None,
                    self._nsb.aind_x0020__project_x0020.CELL__TYPE__LOOKUP__TABLE: None,
                    self._nsb.aind_x0020__project_x0020.COGNITIVE_FLEXIBILITY_IN: None,
                    self._nsb.aind_x0020__project_x0020.CREDIT_ASSIGNMENT_DURING: None,
                    self._nsb.aind_x0020__project_x0020.DYNAMIC__ROUTING: None,
                    self._nsb.aind_x0020__project_x0020.FORCE__FORGING: None,
                    self._nsb.aind_x0020__project_x0020.GENETIC__PERTURBATION__PR: None,
                    self._nsb.aind_x0020__project_x0020.INDICATOR__TESTING: None,
                    self._nsb.aind_x0020__project_x0020.INFORMATION_SEEKING_IN_PA: None,
                    self._nsb.aind_x0020__project_x0020.MEDULLA: None,
                    self._nsb.aind_x0020__project_x0020.MULTIPLEXED_NM: None,
                    self._nsb.aind_x0020__project_x0020.NEUROMODULATOR_CIRCUIT_DY: None,
                    self._nsb.aind_x0020__project_x0020.OPEN_SCOPE: None,
                    self._nsb.aind_x0020__project_x0020.OPHYS_M_FISH__CELL_TYPES: None,
                    self._nsb.aind_x0020__project_x0020.PLACE: None,
                    self._nsb.aind_x0020__project_x0020.SINGLE__NEURON__COMPUTATI: None,
                    self._nsb.aind_x0020__project_x0020.THALAMUS: None,
                    self._nsb.aind_x0020__project_x0020.THALAMUS_AIND__SCIENTIFIC: None,
                }.get(self._nsb.aind_x0020__project_x0020, None)
            )
    
        @property
        def aind_ap2nd_inj(self) -> Optional[str]:
            """Maps ap2nd_inj to aind model."""
            return self._nsb.ap2nd_inj

    @property
        def aind_burr_x0020_4_x0020__injec_005(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__injec_005 to aind model."""
            return self._nsb.burr_x0020_4_x0020__injec_005

    @property
        def aind_burr_x0020_2_x0020__injec_007(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020__injec_007 to aind model."""
            return self._nsb.burr_x0020_2_x0020__injec_007

    @property
        def aind_behavior_x0020_fip_x0020(self) -> Optional[Any]:
            """Maps behavior_x0020_fip_x0020 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020_fip_x0020 is None
                else {
                    self._nsb.behavior_x0020_fip_x0020.N_A: None,
                    self._nsb.behavior_x0020_fip_x0020.NORMAL: None,
                    self._nsb.behavior_x0020_fip_x0020.AXON: None,
                }.get(self._nsb.behavior_x0020_fip_x0020, None)
            )
    
        @property
        def aind_black_x0020__cement(self) -> Optional[Any]:
            """Maps black_x0020__cement to aind model."""
            return (
                None
                if self._nsb.black_x0020__cement is None
                else {
                    self._nsb.black_x0020__cement.YES: None,
                    self._nsb.black_x0020__cement.NO: None,
                }.get(self._nsb.black_x0020__cement, None)
            )
    
        @property
        def aind_breg2_lamb(self) -> Optional[str]:
            """Maps breg2_lamb to aind model."""
            return self._nsb.breg2_lamb

    @property
        def aind_behavior_x0020__autotrain(self) -> Optional[Any]:
            """Maps behavior_x0020__autotrain to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__autotrain is None
                else {
                    self._nsb.behavior_x0020__autotrain.COUPLED__BAITING: None,
                    self._nsb.behavior_x0020__autotrain.UNCOUPLED__BAITING: None,
                    self._nsb.behavior_x0020__autotrain.UNCOUPLED__WITHOUT__BAITI: None,
                    self._nsb.behavior_x0020__autotrain.N_A: None,
                }.get(self._nsb.behavior_x0020__autotrain, None)
            )
    
        @property
        def aind_behavior_x0020__complete(self) -> Optional[str]:
            """Maps behavior_x0020__complete to aind model."""
            return self._nsb.behavior_x0020__complete

    @property
        def aind_burr_x0020_2_x0020__injec_003(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020__injec_003 to aind model."""
            return self._nsb.burr_x0020_2_x0020__injec_003

    @property
        def aind_behavior_x0020__first_x00(self) -> Optional[Any]:
            """Maps behavior_x0020__first_x00 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__first_x00 is None
                else {
                    self._nsb.behavior_x0020__first_x00.N_1_1: None,
                    self._nsb.behavior_x0020__first_x00.N_1_2: None,
                    self._nsb.behavior_x0020__first_x00.N_2: None,
                    self._nsb.behavior_x0020__first_x00.N_3: None,
                    self._nsb.behavior_x0020__first_x00.N_4: None,
                    self._nsb.behavior_x0020__first_x00.N_5: None,
                    self._nsb.behavior_x0020__first_x00.N_6: None,
                    self._nsb.behavior_x0020__first_x00.FINAL: None,
                    self._nsb.behavior_x0020__first_x00.GRADUATED: None,
                    self._nsb.behavior_x0020__first_x00.N_A: None,
                }.get(self._nsb.behavior_x0020__first_x00, None)
            )
    
        @property
        def aind_behavior_x0020__first_x00_001(self) -> Optional[Any]:
            """Maps behavior_x0020__first_x00_001 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__first_x00_001 is None
                else {
                    self._nsb.behavior_x0020__first_x00_001.N_1_1: None,
                    self._nsb.behavior_x0020__first_x00_001.N_1_2: None,
                    self._nsb.behavior_x0020__first_x00_001.N_2: None,
                    self._nsb.behavior_x0020__first_x00_001.N_3: None,
                    self._nsb.behavior_x0020__first_x00_001.N_4: None,
                    self._nsb.behavior_x0020__first_x00_001.N_5: None,
                    self._nsb.behavior_x0020__first_x00_001.N_6: None,
                    self._nsb.behavior_x0020__first_x00_001.FINAL: None,
                    self._nsb.behavior_x0020__first_x00_001.GRADUATED: None,
                    self._nsb.behavior_x0020__first_x00_001.N_A: None,
                }.get(self._nsb.behavior_x0020__first_x00_001, None)
            )
    
        @property
        def aind_behavior_x0020__platform(self) -> Optional[Any]:
            """Maps behavior_x0020__platform to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__platform is None
                else {
                    self._nsb.behavior_x0020__platform.MINDSCOPE: None,
                    self._nsb.behavior_x0020__platform.FORAGING: None,
                    self._nsb.behavior_x0020__platform.VR: None,
                }.get(self._nsb.behavior_x0020__platform, None)
            )
    
        @property
        def aind_behavior_x0020__type(self) -> Optional[Any]:
            """Maps behavior_x0020__type to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__type is None
                else {
                    self._nsb.behavior_x0020__type.SELECT: None,
                    self._nsb.behavior_x0020__type.FORAGING: None,
                    self._nsb.behavior_x0020__type.FORAGING_FP: None,
                    self._nsb.behavior_x0020__type.WR__HAB: None,
                    self._nsb.behavior_x0020__type.HAB__ONLY: None,
                }.get(self._nsb.behavior_x0020__type, None)
            )
    
        @property
        def aind_behavior_x0020_fip_x0020(self) -> Optional[Any]:
            """Maps behavior_x0020_fip_x0020 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020_fip_x0020 is None
                else {
                    self._nsb.behavior_x0020_fip_x0020.N_A: None,
                    self._nsb.behavior_x0020_fip_x0020.NORMAL: None,
                    self._nsb.behavior_x0020_fip_x0020.AXON: None,
                }.get(self._nsb.behavior_x0020_fip_x0020, None)
            )
    
        @property
        def aind_black_x0020__cement(self) -> Optional[Any]:
            """Maps black_x0020__cement to aind model."""
            return (
                None
                if self._nsb.black_x0020__cement is None
                else {
                    self._nsb.black_x0020__cement.YES: None,
                    self._nsb.black_x0020__cement.NO: None,
                }.get(self._nsb.black_x0020__cement, None)
            )
    
        @property
        def aind_breg2_lamb(self) -> Optional[str]:
            """Maps breg2_lamb to aind model."""
            return self._nsb.breg2_lamb

    @property
        def aind_burr_x0020_2_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_2_x0020__fiber.STANDARD__PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_2_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_2_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020__injec to aind model."""
            return self._nsb.burr_x0020_2_x0020__injec

    @property
        def aind_burr_x0020_3_x0020_intend(self) -> Optional[Any]:
            """Maps burr_x0020_3_x0020_intend to aind model."""
            return (
                None
                if self._nsb.burr_x0020_3_x0020_intend is None
                else {
                    self._nsb.burr_x0020_3_x0020_intend.ENTER__CHOICE_1: None,
                    self._nsb.burr_x0020_3_x0020_intend.ENTER__CHOICE_2: None,
                    self._nsb.burr_x0020_3_x0020_intend.ENTER__CHOICE_3: None,
                }.get(self._nsb.burr_x0020_3_x0020_intend, None)
            )
    
        @property
        def aind_burr_x0020_3_x0020_intend_001(self) -> Optional[Any]:
            """Maps burr_x0020_3_x0020_intend_001 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_3_x0020_intend_001 is None
                else {
                    self._nsb.burr_x0020_3_x0020_intend_001.N_A: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.DOPAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.SEROTONIN: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.HISTAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.GLUTAMATE: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.GABA: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.CALCIUM: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.VOLTAGE: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.CONTROL: None,
                }.get(self._nsb.burr_x0020_3_x0020_intend_001, None)
            )
    
        @property
        def aind_burr_x0020_3_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_3_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_3_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_3_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_3_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_3_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_3_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_3_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_3_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_3_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_4_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__angle to aind model."""
            return self._nsb.burr_x0020_4_x0020__angle

    @property
        def aind_burr_x0020_4_x0020__hemis(self) -> Optional[Any]:
            """Maps burr_x0020_4_x0020__hemis to aind model."""
            return (
                None
                if self._nsb.burr_x0020_4_x0020__hemis is None
                else {
                    self._nsb.burr_x0020_4_x0020__hemis.SELECT: None,
                    self._nsb.burr_x0020_4_x0020__hemis.LEFT: None,
                    self._nsb.burr_x0020_4_x0020__hemis.RIGHT: None,
                }.get(self._nsb.burr_x0020_4_x0020__hemis, None)
            )
    
        @property
        def aind_burr_x0020_4_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__injec to aind model."""
            return self._nsb.burr_x0020_4_x0020__injec

    @property
        def aind_burr_x0020_1_x0020_d_x002(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020_d_x002 to aind model."""
            return self._nsb.burr_x0020_1_x0020_d_x002

    @property
        def aind_behavior_x0020__type(self) -> Optional[Any]:
            """Maps behavior_x0020__type to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__type is None
                else {
                    self._nsb.behavior_x0020__type.SELECT: None,
                    self._nsb.behavior_x0020__type.FORAGING: None,
                    self._nsb.behavior_x0020__type.FORAGING_FP: None,
                    self._nsb.behavior_x0020__type.WR__HAB: None,
                    self._nsb.behavior_x0020__type.HAB__ONLY: None,
                }.get(self._nsb.behavior_x0020__type, None)
            )
    
        @property
        def aind_behavior_x0020_fip_x0020(self) -> Optional[Any]:
            """Maps behavior_x0020_fip_x0020 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020_fip_x0020 is None
                else {
                    self._nsb.behavior_x0020_fip_x0020.N_A: None,
                    self._nsb.behavior_x0020_fip_x0020.NORMAL: None,
                    self._nsb.behavior_x0020_fip_x0020.AXON: None,
                }.get(self._nsb.behavior_x0020_fip_x0020, None)
            )
    
        @property
        def aind_black_x0020__cement(self) -> Optional[Any]:
            """Maps black_x0020__cement to aind model."""
            return (
                None
                if self._nsb.black_x0020__cement is None
                else {
                    self._nsb.black_x0020__cement.YES: None,
                    self._nsb.black_x0020__cement.NO: None,
                }.get(self._nsb.black_x0020__cement, None)
            )
    
        @property
        def aind_breg2_lamb(self) -> Optional[str]:
            """Maps breg2_lamb to aind model."""
            return self._nsb.breg2_lamb

    @property
        def aind_burr_x0020_5_x0020_m_x002(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020_m_x002 to aind model."""
            return self._nsb.burr_x0020_5_x0020_m_x002

    @property
        def aind_burr_x0020_2_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020__injec to aind model."""
            return self._nsb.burr_x0020_2_x0020__injec

    @property
        def aind_burr_x0020_6_x0020_m_x002(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020_m_x002 to aind model."""
            return self._nsb.burr_x0020_6_x0020_m_x002

    @property
        def aind_lab_tracks_x0020__request(self) -> Optional[str]:
            """Maps lab_tracks_x0020__request to aind model."""
            return self._nsb.lab_tracks_x0020__request

    @property
        def aind_burr_x0020_hole_x0020_5(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_5 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_5 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_5.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_5.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_5.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_5.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_5, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_6(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_6 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_6 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_6.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_6.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_6.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_6.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_6, None)
            )
    
        @property
        def aind_care_x0020__moduele(self) -> Optional[Any]:
            """Maps care_x0020__moduele to aind model."""
            return (
                None
                if self._nsb.care_x0020__moduele is None
                else {
                    self._nsb.care_x0020__moduele.SELECT: None,
                    self._nsb.care_x0020__moduele.CM_S_01_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_01_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_03_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_03_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_04_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_04_C_D: None,
                }.get(self._nsb.care_x0020__moduele, None)
            )
    
        @property
        def aind_color_tag(self) -> Optional[str]:
            """Maps color_tag to aind model."""
            return self._nsb.color_tag

    @property
        def aind_protocol(self) -> Optional[Any]:
            """Maps protocol to aind model."""
            return (
                None
                if self._nsb.protocol is None
                else {
                    self._nsb.protocol.SELECT: None,
                    self._nsb.protocol.N_2119__TRAINING_AND_QUAL: None,
                    self._nsb.protocol.N_2201__INTERROGATING_PRO: None,
                    self._nsb.protocol.N_2202__TESTING_AA_VS_IN: None,
                    self._nsb.protocol.N_2204__PRIMARY_NEURON_AN: None,
                    self._nsb.protocol.N_2205__OPTIMIZATION_AND: None,
                    self._nsb.protocol.N_2207__IN__VITRO__BRAIN: None,
                    self._nsb.protocol.N_2212__INVESTIGATING__BR: None,
                    self._nsb.protocol.N_2301__TESTING_OF_ENHANC: None,
                    self._nsb.protocol.N_2304__NEUROSURGERY__BEH: None,
                    self._nsb.protocol.N_2305__IN__VIVO__BRAIN: None,
                    self._nsb.protocol.N_2306__PATCH_SEQ_CHARACT: None,
                    self._nsb.protocol.N_2307__DISSECTING_THE_NE: None,
                    self._nsb.protocol.N_2308__INDUCTION_OF__IMM: None,
                    self._nsb.protocol.N_2401__THE_USE_OF_MICE_F: None,
                    self._nsb.protocol.N_2402__BRAIN__OBSERVATOR: None,
                    self._nsb.protocol.N_2403__ELECTROPHYSIOLOGY: None,
                    self._nsb.protocol.N_2405__ANALYSIS_OF__INTE: None,
                    self._nsb.protocol.N_2406__CHARACTERIZATION: None,
                    self._nsb.protocol.N_2410__VALIDATION_OF_BRA: None,
                    self._nsb.protocol.N_2412__CIRCUIT_TRACING_A: None,
                    self._nsb.protocol.N_2413__NEUROPHYSIOLOGY_O: None,
                    self._nsb.protocol.N_2414__ELECTROPHYSIOLOGI: None,
                    self._nsb.protocol.N_2415__OPTOPHYSIOLOGICAL: None,
                    self._nsb.protocol.N_2416__ANATOMICAL_ANALYS: None,
                    self._nsb.protocol.N_2417__CHARACTERIZATION: None,
                    self._nsb.protocol.N_2418__IN__VITRO__SINGLE: None,
                    self._nsb.protocol.N_2427__OPEN_SCOPE__MINDS: None,
                }.get(self._nsb.protocol, None)
            )
    
        @property
        def aind_ret_setting0(self) -> Optional[Any]:
            """Maps ret_setting0 to aind model."""
            return (
                None
                if self._nsb.ret_setting0 is None
                else {
                    self._nsb.ret_setting0.OFF: None,
                    self._nsb.ret_setting0.ON: None,
                }.get(self._nsb.ret_setting0, None)
            )
    
        @property
        def aind_ret_setting1(self) -> Optional[Any]:
            """Maps ret_setting1 to aind model."""
            return (
                None
                if self._nsb.ret_setting1 is None
                else {
                    self._nsb.ret_setting1.OFF: None,
                    self._nsb.ret_setting1.ON: None,
                }.get(self._nsb.ret_setting1, None)
            )
    
        @property
        def aind_round1_inj_isolevel(self) -> Optional[str]:
            """Maps round1_inj_isolevel to aind model."""
            return self._nsb.round1_inj_isolevel

    @property
        def aind_lab_tracks_x0020__group(self) -> Optional[str]:
            """Maps lab_tracks_x0020__group to aind model."""
            return self._nsb.lab_tracks_x0020__group

    @property
        def aind_burr_x0020_3_x0020__injec_002(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__injec_002 to aind model."""
            return self._nsb.burr_x0020_3_x0020__injec_002

    @property
        def aind_burr_x0020_4_x0020_d_x002_001(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020_d_x002_001 to aind model."""
            return self._nsb.burr_x0020_4_x0020_d_x002_001

    @property
        def aind_burr_x0020_5_x0020_d_x002_002(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020_d_x002_002 to aind model."""
            return self._nsb.burr_x0020_5_x0020_d_x002_002

    @property
        def aind_burr_x0020_hole_x0020_4(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_4 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_4 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_4.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_4.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_4.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_4.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_4, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_5(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_5 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_5 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_5.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_5.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_5.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_5.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_5, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_6(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_6 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_6 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_6.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_6.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_6.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_6.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_6, None)
            )
    
        @property
        def aind_care_x0020__moduele(self) -> Optional[Any]:
            """Maps care_x0020__moduele to aind model."""
            return (
                None
                if self._nsb.care_x0020__moduele is None
                else {
                    self._nsb.care_x0020__moduele.SELECT: None,
                    self._nsb.care_x0020__moduele.CM_S_01_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_01_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_03_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_03_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_04_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_04_C_D: None,
                }.get(self._nsb.care_x0020__moduele, None)
            )
    
        @property
        def aind_color_tag(self) -> Optional[str]:
            """Maps color_tag to aind model."""
            return self._nsb.color_tag

    @property
        def aind_burr5_x0020__status(self) -> Optional[Any]:
            """Maps burr5_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr5_x0020__status is None
                else {
                    self._nsb.burr5_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr5_x0020__status, None)
            )
    
        @property
        def aind_burr5_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr5_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr5_x0020__virus_x0020 is None
                else {
                    self._nsb.burr5_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr5_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr6_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr6_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__injection_x0 is None
                else {
                    self._nsb.burr6_x0020__injection_x0.SELECT: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr6_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr6_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr6_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__perform_x002 is None
                else {
                    self._nsb.burr6_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr6_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr6_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr6_x0020__status(self) -> Optional[Any]:
            """Maps burr6_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__status is None
                else {
                    self._nsb.burr6_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr6_x0020__status, None)
            )
    
        @property
        def aind_burr6_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr6_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__virus_x0020 is None
                else {
                    self._nsb.burr6_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr6_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_1_x0020__fiber.STANDARD_PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_1_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_1_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__grid(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__grid to aind model."""
            return self._nsb.burr_x0020_1_x0020__grid

    @property
        def aind_burr_x0020_5_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__angle to aind model."""
            return self._nsb.burr_x0020_5_x0020__angle

    @property
        def aind_burr_x0020_2_x0020__injec_002(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020__injec_002 to aind model."""
            return self._nsb.burr_x0020_2_x0020__injec_002

    @property
        def aind_burr_x0020_6_x0020__injec_003(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020__injec_003 to aind model."""
            return self._nsb.burr_x0020_6_x0020__injec_003

    @property
        def aind_date_x0020_of_x0020__birt(self) -> Optional[str]:
            """Maps date_x0020_of_x0020__birt to aind model."""
            return self._nsb.date_x0020_of_x0020__birt

    @property
        def aind_burr_x0020_4_x0020__injec_004(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__injec_004 to aind model."""
            return self._nsb.burr_x0020_4_x0020__injec_004

    @property
        def aind_burr_x0020_3_x0020__injec_004(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__injec_004 to aind model."""
            return self._nsb.burr_x0020_3_x0020__injec_004

    @property
        def aind_burr_x0020_5_x0020__injec_006(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__injec_006 to aind model."""
            return self._nsb.burr_x0020_5_x0020__injec_006

    @property
        def aind_fiber_x0020__implant3_x00(self) -> Optional[Any]:
            """Maps fiber_x0020__implant3_x00 to aind model."""
            return (
                None
                if self._nsb.fiber_x0020__implant3_x00 is None
                else {
                    self._nsb.fiber_x0020__implant3_x00.SELECT: None,
                    self._nsb.fiber_x0020__implant3_x00.N_1_0_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_1_5_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_2_0_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_2_5_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_3_0_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_3_5_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_4_0_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_4_5_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_5_0_MM: None,
                }.get(self._nsb.fiber_x0020__implant3_x00, None)
            )
    
        @property
        def aind_fiber_x0020__implant3_x00_001(self) -> Optional[str]:
            """Maps fiber_x0020__implant3_x00_001 to aind model."""
            return self._nsb.fiber_x0020__implant3_x00_001

    @property
        def aind_burr_x0020_5_x0020__inten(self) -> Optional[Any]:
            """Maps burr_x0020_5_x0020__inten to aind model."""
            return (
                None
                if self._nsb.burr_x0020_5_x0020__inten is None
                else {
                    self._nsb.burr_x0020_5_x0020__inten.FRP__FRONTAL_POLE_CEREBRA: None,
                    self._nsb.burr_x0020_5_x0020__inten.M_OP__PRIMARY_MOTOR_AREA: None,
                    self._nsb.burr_x0020_5_x0020__inten.M_OS__SECONDARY_MOTOR_ARE: None,
                    self._nsb.burr_x0020_5_x0020__inten.S_SP_N__PRIMARY_SOMATOSEN: None,
                    self._nsb.burr_x0020_5_x0020__inten.S_SP_BFD__PRIMARY_SOMATOS: None,
                    self._nsb.burr_x0020_5_x0020__inten.S_SP_LL__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_5_x0020__inten.S_SP_M__PRIMARY_SOMATOSEN: None,
                    self._nsb.burr_x0020_5_x0020__inten.S_SP_UL__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_5_x0020__inten.S_SP_TR__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_5_x0020__inten.S_SP_UN__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_5_x0020__inten.S_SS__SUPPLEMENTAL_SOMATO: None,
                    self._nsb.burr_x0020_5_x0020__inten.GU__GUSTATORY_AREAS: None,
                    self._nsb.burr_x0020_5_x0020__inten.VISC__VISCERAL_AREA: None,
                    self._nsb.burr_x0020_5_x0020__inten.AU_DD__DORSAL_AUDITORY_AR: None,
                    self._nsb.burr_x0020_5_x0020__inten.AU_DP__PRIMARY_AUDITORY_A: None,
                    self._nsb.burr_x0020_5_x0020__inten.AU_DPO__POSTERIOR_AUDITOR: None,
                    self._nsb.burr_x0020_5_x0020__inten.AU_DV__VENTRAL_AUDITORY_A: None,
                    self._nsb.burr_x0020_5_x0020__inten.VI_SAL__ANTEROLATERAL_VIS: None,
                    self._nsb.burr_x0020_5_x0020__inten.VI_SAM__ANTEROMEDIAL_VISU: None,
                    self._nsb.burr_x0020_5_x0020__inten.VI_SL__LATERAL_VISUAL_ARE: None,
                    self._nsb.burr_x0020_5_x0020__inten.VI_SP__PRIMARY_VISUAL_ARE: None,
                    self._nsb.burr_x0020_5_x0020__inten.VI_SPL__POSTEROLATERAL_VI: None,
                    self._nsb.burr_x0020_5_x0020__inten.VI_SPM_POSTEROMEDIAL_VISU: None,
                    self._nsb.burr_x0020_5_x0020__inten.VI_SLI__LATEROINTERMEDIAT: None,
                    self._nsb.burr_x0020_5_x0020__inten.VI_SPOR__POSTRHINAL_AREA: None,
                    self._nsb.burr_x0020_5_x0020__inten.AC_AD__ANTERIOR_CINGULATE: None,
                    self._nsb.burr_x0020_5_x0020__inten.AC_AV__ANTERIOR_CINGULATE: None,
                    self._nsb.burr_x0020_5_x0020__inten.PL__PRELIMBIC_AREA: None,
                    self._nsb.burr_x0020_5_x0020__inten.ILA__INFRALIMBIC_AREA: None,
                    self._nsb.burr_x0020_5_x0020__inten.OR_BL__ORBITAL_AREA_LATER: None,
                    self._nsb.burr_x0020_5_x0020__inten.OR_BM__ORBITAL_AREA_MEDIA: None,
                    self._nsb.burr_x0020_5_x0020__inten.OR_BV__ORBITAL_AREA_VENTR: None,
                    self._nsb.burr_x0020_5_x0020__inten.OR_BVL__ORBITAL_AREA_VENT: None,
                    self._nsb.burr_x0020_5_x0020__inten.A_ID__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_5_x0020__inten.A_IP__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_5_x0020__inten.A_IV__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_5_x0020__inten.RS_PAGL__RETROSPLENIAL_AR: None,
                    self._nsb.burr_x0020_5_x0020__inten.RS_PD__RETROSPLENIAL_AREA: None,
                    self._nsb.burr_x0020_5_x0020__inten.RS_PV__RETROSPLENIAL_AREA: None,
                    self._nsb.burr_x0020_5_x0020__inten.VI_SA__ANTERIOR_AREA: None,
                    self._nsb.burr_x0020_5_x0020__inten.VI_SRL__ROSTROLATERAL_VIS: None,
                    self._nsb.burr_x0020_5_x0020__inten.T_EA__TEMPORAL_ASSOCIATIO: None,
                    self._nsb.burr_x0020_5_x0020__inten.PERI__PERIRHINAL_AREA: None,
                    self._nsb.burr_x0020_5_x0020__inten.ECT__ECTORHINAL_AREA: None,
                    self._nsb.burr_x0020_5_x0020__inten.MOB__MAIN_OLFACTORY_BULB: None,
                    self._nsb.burr_x0020_5_x0020__inten.AOB__ACCESSORY_OLFACTORY: None,
                    self._nsb.burr_x0020_5_x0020__inten.AON__ANTERIOR_OLFACTORY_N: None,
                    self._nsb.burr_x0020_5_x0020__inten.T_TD__TAENIA_TECTA_DORSAL: None,
                    self._nsb.burr_x0020_5_x0020__inten.T_TV__TAENIA_TECTA_VENTRA: None,
                    self._nsb.burr_x0020_5_x0020__inten.DP__DORSAL_PEDUNCULAR_ARE: None,
                    self._nsb.burr_x0020_5_x0020__inten.PIR__PIRIFORM_AREA: None,
                    self._nsb.burr_x0020_5_x0020__inten.NLOT__NUCLEUS_OF_THE_LATE: None,
                    self._nsb.burr_x0020_5_x0020__inten.CO_AA__CORTICAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_5_x0020__inten.CO_AP__CORTICAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_5_x0020__inten.PAA__PIRIFORM_AMYGDALAR_A: None,
                    self._nsb.burr_x0020_5_x0020__inten.TR__POSTPIRIFORM_TRANSITI: None,
                    self._nsb.burr_x0020_5_x0020__inten.CA1__FIELD_CA1: None,
                    self._nsb.burr_x0020_5_x0020__inten.CA2__FIELD_CA2: None,
                    self._nsb.burr_x0020_5_x0020__inten.CA3__FIELD_CA3: None,
                    self._nsb.burr_x0020_5_x0020__inten.DG__DENTATE_GYRUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.FC__FASCIOLA_CINEREA: None,
                    self._nsb.burr_x0020_5_x0020__inten.IG__INDUSEUM_GRISEUM: None,
                    self._nsb.burr_x0020_5_x0020__inten.EN_TL__ENTORHINAL_AREA_LA: None,
                    self._nsb.burr_x0020_5_x0020__inten.EN_TM__ENTORHINAL_AREA_ME: None,
                    self._nsb.burr_x0020_5_x0020__inten.PAR__PARASUBICULUM: None,
                    self._nsb.burr_x0020_5_x0020__inten.POST__POSTSUBICULUM: None,
                    self._nsb.burr_x0020_5_x0020__inten.PRE__PRESUBICULUM: None,
                    self._nsb.burr_x0020_5_x0020__inten.SUB__SUBICULUM: None,
                    self._nsb.burr_x0020_5_x0020__inten.PRO_S__PROSUBICULUM: None,
                    self._nsb.burr_x0020_5_x0020__inten.HATA__HIPPOCAMPO_AMYGDALA: None,
                    self._nsb.burr_x0020_5_x0020__inten.A_PR__AREA_PROSTRIATA: None,
                    self._nsb.burr_x0020_5_x0020__inten.CLA__CLAUSTRUM: None,
                    self._nsb.burr_x0020_5_x0020__inten.E_PD__ENDOPIRIFORM_NUCLEU: None,
                    self._nsb.burr_x0020_5_x0020__inten.E_PV__ENDOPIRIFORM_NUCLEU: None,
                    self._nsb.burr_x0020_5_x0020__inten.LA__LATERAL_AMYGDALAR_NUC: None,
                    self._nsb.burr_x0020_5_x0020__inten.BLA__BASOLATERAL_AMYGDALA: None,
                    self._nsb.burr_x0020_5_x0020__inten.BMA__BASOMEDIAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_5_x0020__inten.PA__POSTERIOR_AMYGDALAR_N: None,
                    self._nsb.burr_x0020_5_x0020__inten.CP__CAUDOPUTAMEN: None,
                    self._nsb.burr_x0020_5_x0020__inten.ACB__NUCLEUS_ACCUMBENS: None,
                    self._nsb.burr_x0020_5_x0020__inten.FS__FUNDUS_OF_STRIATUM: None,
                    self._nsb.burr_x0020_5_x0020__inten.OT__OLFACTORY_TUBERCLE: None,
                    self._nsb.burr_x0020_5_x0020__inten.L_SC__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.L_SR__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.L_SV__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.SF__SEPTOFIMBRIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.SH__SEPTOHIPPOCAMPAL_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.AAA__ANTERIOR_AMYGDALAR_A: None,
                    self._nsb.burr_x0020_5_x0020__inten.BA__BED_NUCLEUS_OF_THE_AC: None,
                    self._nsb.burr_x0020_5_x0020__inten.CEA__CENTRAL_AMYGDALAR_NU: None,
                    self._nsb.burr_x0020_5_x0020__inten.IA__INTERCALATED_AMYGDALA: None,
                    self._nsb.burr_x0020_5_x0020__inten.MEA__MEDIAL_AMYGDALAR_NUC: None,
                    self._nsb.burr_x0020_5_x0020__inten.G_PE__GLOBUS_PALLIDUS_EXT: None,
                    self._nsb.burr_x0020_5_x0020__inten.G_PI__GLOBUS_PALLIDUS_INT: None,
                    self._nsb.burr_x0020_5_x0020__inten.SI__SUBSTANTIA_INNOMINATA: None,
                    self._nsb.burr_x0020_5_x0020__inten.MA__MAGNOCELLULAR_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.MS__MEDIAL_SEPTAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.NDB__DIAGONAL_BAND_NUCLEU: None,
                    self._nsb.burr_x0020_5_x0020__inten.TRS__TRIANGULAR_NUCLEUS_O: None,
                    self._nsb.burr_x0020_5_x0020__inten.BST__BED_NUCLEI_OF_THE_ST: None,
                    self._nsb.burr_x0020_5_x0020__inten.VAL__VENTRAL_ANTERIOR_LAT: None,
                    self._nsb.burr_x0020_5_x0020__inten.VM__VENTRAL_MEDIAL_NUCLEU: None,
                    self._nsb.burr_x0020_5_x0020__inten.VPL__VENTRAL_POSTEROLATER: None,
                    self._nsb.burr_x0020_5_x0020__inten.VP_LPC__VENTRAL_POSTEROLA: None,
                    self._nsb.burr_x0020_5_x0020__inten.VPM__VENTRAL_POSTEROMEDIA: None,
                    self._nsb.burr_x0020_5_x0020__inten.VP_MPC__VENTRAL_POSTEROME: None,
                    self._nsb.burr_x0020_5_x0020__inten.PO_T__POSTERIOR_TRIANGULA: None,
                    self._nsb.burr_x0020_5_x0020__inten.SPF__SUBPARAFASCICULAR_NU: None,
                    self._nsb.burr_x0020_5_x0020__inten.SPA__SUBPARAFASCICULAR_AR: None,
                    self._nsb.burr_x0020_5_x0020__inten.PP__PERIPEDUNCULAR_NUCLEU: None,
                    self._nsb.burr_x0020_5_x0020__inten.MG__MEDIAL_GENICULATE_COM: None,
                    self._nsb.burr_x0020_5_x0020__inten.L_GD__DORSAL_PART_OF_THE: None,
                    self._nsb.burr_x0020_5_x0020__inten.LP__LATERAL_POSTERIOR_NUC: None,
                    self._nsb.burr_x0020_5_x0020__inten.PO__POSTERIOR_COMPLEX_OF: None,
                    self._nsb.burr_x0020_5_x0020__inten.POL__POSTERIOR_LIMITING_N: None,
                    self._nsb.burr_x0020_5_x0020__inten.SGN__SUPRAGENICULATE_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.ETH__ETHMOID_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_5_x0020__inten.AV__ANTEROVENTRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.AM__ANTEROMEDIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.AD__ANTERODORSAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.IAM__INTERANTEROMEDIAL_NU: None,
                    self._nsb.burr_x0020_5_x0020__inten.IAD__INTERANTERODORSAL_NU: None,
                    self._nsb.burr_x0020_5_x0020__inten.LD__LATERAL_DORSAL_NUCLEU: None,
                    self._nsb.burr_x0020_5_x0020__inten.IMD__INTERMEDIODORSAL_NUC: None,
                    self._nsb.burr_x0020_5_x0020__inten.MD__MEDIODORSAL_NUCLEUS_O: None,
                    self._nsb.burr_x0020_5_x0020__inten.SMT__SUBMEDIAL_NUCLEUS_OF: None,
                    self._nsb.burr_x0020_5_x0020__inten.PR__PERIREUNENSIS_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.PVT__PARAVENTRICULAR_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.PT__PARATAENIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.RE__NUCLEUS_OF_REUNIENS: None,
                    self._nsb.burr_x0020_5_x0020__inten.XI__XIPHOID_THALAMIC_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.RH__RHOMBOID_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.CM__CENTRAL_MEDIAL_NUCLEU: None,
                    self._nsb.burr_x0020_5_x0020__inten.PCN__PARACENTRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.CL__CENTRAL_LATERAL_NUCLE: None,
                    self._nsb.burr_x0020_5_x0020__inten.PF__PARAFASCICULAR_NUCLEU: None,
                    self._nsb.burr_x0020_5_x0020__inten.PIL__POSTERIOR_INTRALAMIN: None,
                    self._nsb.burr_x0020_5_x0020__inten.RT__RETICULAR_NUCLEUS_OF: None,
                    self._nsb.burr_x0020_5_x0020__inten.IGL__INTERGENICULATE_LEAF: None,
                    self._nsb.burr_x0020_5_x0020__inten.INT_G__INTERMEDIATE_GENIC: None,
                    self._nsb.burr_x0020_5_x0020__inten.L_GV__VENTRAL_PART_OF_THE: None,
                    self._nsb.burr_x0020_5_x0020__inten.SUB_G__SUBGENICULATE_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.MH__MEDIAL_HABENULA: None,
                    self._nsb.burr_x0020_5_x0020__inten.LH__LATERAL_HABENULA: None,
                    self._nsb.burr_x0020_5_x0020__inten.SO__SUPRAOPTIC_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.PVH__PARAVENTRICULAR_HYPO: None,
                    self._nsb.burr_x0020_5_x0020__inten.P_VA__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_5_x0020__inten.P_VI__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_5_x0020__inten.ARH__ARCUATE_HYPOTHALAMIC: None,
                    self._nsb.burr_x0020_5_x0020__inten.ADP__ANTERODORSAL_PREOPTI: None,
                    self._nsb.burr_x0020_5_x0020__inten.AVP__ANTEROVENTRAL_PREOPT: None,
                    self._nsb.burr_x0020_5_x0020__inten.AVPV__ANTEROVENTRAL_PERIV: None,
                    self._nsb.burr_x0020_5_x0020__inten.DMH__DORSOMEDIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.MEPO__MEDIAN_PREOPTIC_NUC: None,
                    self._nsb.burr_x0020_5_x0020__inten.MPO__MEDIAL_PREOPTIC_AREA: None,
                    self._nsb.burr_x0020_5_x0020__inten.PS__PARASTRIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.P_VP__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_5_x0020__inten.P_VPO__PERIVENTRICULAR_HY: None,
                    self._nsb.burr_x0020_5_x0020__inten.SBPV__SUBPARAVENTRICULAR: None,
                    self._nsb.burr_x0020_5_x0020__inten.SCH__SUPRACHIASMATIC_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.SFO__SUBFORNICAL_ORGAN: None,
                    self._nsb.burr_x0020_5_x0020__inten.VMPO__VENTROMEDIAL_PREOPT: None,
                    self._nsb.burr_x0020_5_x0020__inten.VLPO__VENTROLATERAL_PREOP: None,
                    self._nsb.burr_x0020_5_x0020__inten.AHN__ANTERIOR_HYPOTHALAMI: None,
                    self._nsb.burr_x0020_5_x0020__inten.LM__LATERAL_MAMMILLARY_NU: None,
                    self._nsb.burr_x0020_5_x0020__inten.MM__MEDIAL_MAMMILLARY_NUC: None,
                    self._nsb.burr_x0020_5_x0020__inten.SUM__SUPRAMAMMILLARY_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.TM__TUBEROMAMMILLARY_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.MPN__MEDIAL_PREOPTIC_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.P_MD__DORSAL_PREMAMMILLAR: None,
                    self._nsb.burr_x0020_5_x0020__inten.P_MV__VENTRAL_PREMAMMILLA: None,
                    self._nsb.burr_x0020_5_x0020__inten.PV_HD__PARAVENTRICULAR_HY: None,
                    self._nsb.burr_x0020_5_x0020__inten.VMH__VENTROMEDIAL_HYPOTHA: None,
                    self._nsb.burr_x0020_5_x0020__inten.PH__POSTERIOR_HYPOTHALAMI: None,
                    self._nsb.burr_x0020_5_x0020__inten.LHA__LATERAL_HYPOTHALAMIC: None,
                    self._nsb.burr_x0020_5_x0020__inten.LPO__LATERAL_PREOPTIC_ARE: None,
                    self._nsb.burr_x0020_5_x0020__inten.PSTN__PARASUBTHALAMIC_NUC: None,
                    self._nsb.burr_x0020_5_x0020__inten.PE_F__PERIFORNICAL_NUCLEU: None,
                    self._nsb.burr_x0020_5_x0020__inten.RCH__RETROCHIASMATIC_AREA: None,
                    self._nsb.burr_x0020_5_x0020__inten.STN__SUBTHALAMIC_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.TU__TUBERAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.ZI__ZONA_INCERTA: None,
                    self._nsb.burr_x0020_5_x0020__inten.S_CS__SUPERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.IC__INFERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.NB__NUCLEUS_OF_THE_BRACHI: None,
                    self._nsb.burr_x0020_5_x0020__inten.SAG__NUCLEUS_SAGULUM: None,
                    self._nsb.burr_x0020_5_x0020__inten.PBG__PARABIGEMINAL_NUCLEU: None,
                    self._nsb.burr_x0020_5_x0020__inten.S_NR__SUBSTANTIA_NIGRA_RE: None,
                    self._nsb.burr_x0020_5_x0020__inten.VTA__VENTRAL_TEGMENTAL_AR: None,
                    self._nsb.burr_x0020_5_x0020__inten.PN__PARANIGRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.RR__MIDBRAIN_RETICULAR_NU: None,
                    self._nsb.burr_x0020_5_x0020__inten.MRN__MIDBRAIN_RETICULAR_N: None,
                    self._nsb.burr_x0020_5_x0020__inten.S_CM__SUPERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.PAG__PERIAQUEDUCTAL_GRAY: None,
                    self._nsb.burr_x0020_5_x0020__inten.APN__ANTERIOR_PRETECTAL_N: None,
                    self._nsb.burr_x0020_5_x0020__inten.MPT__MEDIAL_PRETECTAL_ARE: None,
                    self._nsb.burr_x0020_5_x0020__inten.NOT__NUCLEUS_OF_THE_OPTIC: None,
                    self._nsb.burr_x0020_5_x0020__inten.NPC__NUCLEUS_OF_THE_POSTE: None,
                    self._nsb.burr_x0020_5_x0020__inten.OP__OLIVARY_PRETECTAL_NUC: None,
                    self._nsb.burr_x0020_5_x0020__inten.PPT__POSTERIOR_PRETECTAL: None,
                    self._nsb.burr_x0020_5_x0020__inten.RPF__RETROPARAFASCICULAR: None,
                    self._nsb.burr_x0020_5_x0020__inten.CUN__CUNEIFORM_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.RN__RED_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.III__OCULOMOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.MA3__MEDIAL_ACCESORY_OCUL: None,
                    self._nsb.burr_x0020_5_x0020__inten.EW__EDINGER__WESTPHAL_NUC: None,
                    self._nsb.burr_x0020_5_x0020__inten.IV__TROCHLEAR_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.PA4__PARATROCHLEAR_NUCLEU: None,
                    self._nsb.burr_x0020_5_x0020__inten.VTN__VENTRAL_TEGMENTAL_NU: None,
                    self._nsb.burr_x0020_5_x0020__inten.AT__ANTERIOR_TEGMENTAL_NU: None,
                    self._nsb.burr_x0020_5_x0020__inten.LT__LATERAL_TERMINAL_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.DT__DORSAL_TERMINAL_NUCLE: None,
                    self._nsb.burr_x0020_5_x0020__inten.MT__MEDIAL_TERMINAL_NUCLE: None,
                    self._nsb.burr_x0020_5_x0020__inten.S_NC__SUBSTANTIA_NIGRA_CO: None,
                    self._nsb.burr_x0020_5_x0020__inten.PPN__PEDUNCULOPONTINE_NUC: None,
                    self._nsb.burr_x0020_5_x0020__inten.IF__INTERFASCICULAR_NUCLE: None,
                    self._nsb.burr_x0020_5_x0020__inten.IPN__INTERPEDUNCULAR_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.RL__ROSTRAL_LINEAR_NUCLEU: None,
                    self._nsb.burr_x0020_5_x0020__inten.CLI__CENTRAL_LINEAR_NUCLE: None,
                    self._nsb.burr_x0020_5_x0020__inten.DR__DORSAL_NUCLEUS_RAPHE: None,
                    self._nsb.burr_x0020_5_x0020__inten.NLL__NUCLEUS_OF_THE_LATER: None,
                    self._nsb.burr_x0020_5_x0020__inten.PSV__PRINCIPAL_SENSORY_NU: None,
                    self._nsb.burr_x0020_5_x0020__inten.PB__PARABRACHIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.SOC__SUPERIOR_OLIVARY_COM: None,
                    self._nsb.burr_x0020_5_x0020__inten.B__BARRINGTON_S_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.DTN__DORSAL_TEGMENTAL_NUC: None,
                    self._nsb.burr_x0020_5_x0020__inten.PD_TG__POSTERODORSAL_TEGM: None,
                    self._nsb.burr_x0020_5_x0020__inten.PCG__PONTINE_CENTRAL_GRAY: None,
                    self._nsb.burr_x0020_5_x0020__inten.PG__PONTINE_GRAY: None,
                    self._nsb.burr_x0020_5_x0020__inten.PR_NC__PONTINE_RETICULAR: None,
                    self._nsb.burr_x0020_5_x0020__inten.SG__SUPRAGENUAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.SUT__SUPRATRIGEMINAL_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.TRN__TEGMENTAL_RETICULAR: None,
                    self._nsb.burr_x0020_5_x0020__inten.V__MOTOR_NUCLEUS_OF_TRIGE: None,
                    self._nsb.burr_x0020_5_x0020__inten.P5__PERITRIGEMINAL_ZONE: None,
                    self._nsb.burr_x0020_5_x0020__inten.ACS5__ACCESSORY_TRIGEMINA: None,
                    self._nsb.burr_x0020_5_x0020__inten.PC5__PARVICELLULAR_MOTOR: None,
                    self._nsb.burr_x0020_5_x0020__inten.I5__INTERTRIGEMINAL_NUCLE: None,
                    self._nsb.burr_x0020_5_x0020__inten.CS__SUPERIOR_CENTRAL_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.LC__LOCUS_CERULEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.LDT__LATERODORSAL_TEGMENT: None,
                    self._nsb.burr_x0020_5_x0020__inten.NI__NUCLEUS_INCERTUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.PR_NR__PONTINE_RETICULAR: None,
                    self._nsb.burr_x0020_5_x0020__inten.RPO__NUCLEUS_RAPHE_PONTIS: None,
                    self._nsb.burr_x0020_5_x0020__inten.SLC__SUBCERULEUS_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.SLD__SUBLATERODORSAL_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.MY__MEDULLA: None,
                    self._nsb.burr_x0020_5_x0020__inten.AP__AREA_POSTREMA: None,
                    self._nsb.burr_x0020_5_x0020__inten.DCO__DORSAL_COCHLEAR_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.VCO__VENTRAL_COCHLEAR_NUC: None,
                    self._nsb.burr_x0020_5_x0020__inten.CU__CUNEATE_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.GR__GRACILE_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.ECU__EXTERNAL_CUNEATE_NUC: None,
                    self._nsb.burr_x0020_5_x0020__inten.NTB__NUCLEUS_OF_THE_TRAPE: None,
                    self._nsb.burr_x0020_5_x0020__inten.NTS__NUCLEUS_OF_THE_SOLIT: None,
                    self._nsb.burr_x0020_5_x0020__inten.SPVC__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_5_x0020__inten.SPVI__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_5_x0020__inten.SPVO__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_5_x0020__inten.PA5__PARATRIGEMINAL_NUCLE: None,
                    self._nsb.burr_x0020_5_x0020__inten.VI__ABDUCENS_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.VII__FACIAL_MOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.AMB__NUCLEUS_AMBIGUUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.DMX__DORSAL_MOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.GRN__GIGANTOCELLULAR_RETI: None,
                    self._nsb.burr_x0020_5_x0020__inten.ICB__INFRACEREBELLAR_NUCL: None,
                    self._nsb.burr_x0020_5_x0020__inten.IO__INFERIOR_OLIVARY_COMP: None,
                    self._nsb.burr_x0020_5_x0020__inten.IRN__INTERMEDIATE_RETICUL: None,
                    self._nsb.burr_x0020_5_x0020__inten.ISN__INFERIOR_SALIVATORY: None,
                    self._nsb.burr_x0020_5_x0020__inten.LIN__LINEAR_NUCLEUS_OF_TH: None,
                    self._nsb.burr_x0020_5_x0020__inten.LRN__LATERAL_RETICULAR_NU: None,
                    self._nsb.burr_x0020_5_x0020__inten.MARN__MAGNOCELLULAR_RETIC: None,
                    self._nsb.burr_x0020_5_x0020__inten.MDRN__MEDULLARY_RETICULAR: None,
                    self._nsb.burr_x0020_5_x0020__inten.PARN__PARVICELLULAR_RETIC: None,
                    self._nsb.burr_x0020_5_x0020__inten.PAS__PARASOLITARY_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.PGRN__PARAGIGANTOCELLULAR: None,
                    self._nsb.burr_x0020_5_x0020__inten.NR__NUCLEUS_OF__ROLLER: None,
                    self._nsb.burr_x0020_5_x0020__inten.PRP__NUCLEUS_PREPOSITUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.PMR__PARAMEDIAN_RETICULAR: None,
                    self._nsb.burr_x0020_5_x0020__inten.PPY__PARAPYRAMIDAL_NUCLEU: None,
                    self._nsb.burr_x0020_5_x0020__inten.LAV__LATERAL_VESTIBULAR_N: None,
                    self._nsb.burr_x0020_5_x0020__inten.MV__MEDIAL_VESTIBULAR_NUC: None,
                    self._nsb.burr_x0020_5_x0020__inten.SPIV__SPINAL_VESTIBULAR_N: None,
                    self._nsb.burr_x0020_5_x0020__inten.SUV__SUPERIOR_VESTIBULAR: None,
                    self._nsb.burr_x0020_5_x0020__inten.X__NUCLEUS_X: None,
                    self._nsb.burr_x0020_5_x0020__inten.XII__HYPOGLOSSAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.Y__NUCLEUS_Y: None,
                    self._nsb.burr_x0020_5_x0020__inten.RM__NUCLEUS_RAPHE_MAGNUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.RPA__NUCLEUS_RAPHE_PALLID: None,
                    self._nsb.burr_x0020_5_x0020__inten.RO__NUCLEUS_RAPHE_OBSCURU: None,
                    self._nsb.burr_x0020_5_x0020__inten.LING__LINGULA_I: None,
                    self._nsb.burr_x0020_5_x0020__inten.CENT2__LOBULE_II: None,
                    self._nsb.burr_x0020_5_x0020__inten.CENT3__LOBULE_III: None,
                    self._nsb.burr_x0020_5_x0020__inten.CUL4_5__LOBULES_IV_V: None,
                    self._nsb.burr_x0020_5_x0020__inten.DEC__DECLIVE_VI: None,
                    self._nsb.burr_x0020_5_x0020__inten.FOTU__FOLIUM_TUBER_VERMIS: None,
                    self._nsb.burr_x0020_5_x0020__inten.PYR__PYRAMUS_VIII: None,
                    self._nsb.burr_x0020_5_x0020__inten.UVU__UVULA_IX: None,
                    self._nsb.burr_x0020_5_x0020__inten.NOD__NODULUS_X: None,
                    self._nsb.burr_x0020_5_x0020__inten.SIM__SIMPLE_LOBULE: None,
                    self._nsb.burr_x0020_5_x0020__inten.A_NCR1__CRUS_1: None,
                    self._nsb.burr_x0020_5_x0020__inten.A_NCR2__CRUS_2: None,
                    self._nsb.burr_x0020_5_x0020__inten.PRM__PARAMEDIAN_LOBULE: None,
                    self._nsb.burr_x0020_5_x0020__inten.COPY__COPULA_PYRAMIDIS: None,
                    self._nsb.burr_x0020_5_x0020__inten.PFL__PARAFLOCCULUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.FL__FLOCCULUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.FN__FASTIGIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.IP__INTERPOSED_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.DN__DENTATE_NUCLEUS: None,
                    self._nsb.burr_x0020_5_x0020__inten.VE_CB__VESTIBULOCEREBELLA: None,
                }.get(self._nsb.burr_x0020_5_x0020__inten, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020_a_x002(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020_a_x002 to aind model."""
            return self._nsb.burr_x0020_5_x0020_a_x002

    @property
        def aind_fiber_x0020__implant6_x00(self) -> Optional[Any]:
            """Maps fiber_x0020__implant6_x00 to aind model."""
            return (
                None
                if self._nsb.fiber_x0020__implant6_x00 is None
                else {
                    self._nsb.fiber_x0020__implant6_x00.SELECT: None,
                    self._nsb.fiber_x0020__implant6_x00.N_1_0_MM: None,
                    self._nsb.fiber_x0020__implant6_x00.N_1_5_MM: None,
                    self._nsb.fiber_x0020__implant6_x00.N_2_0_MM: None,
                    self._nsb.fiber_x0020__implant6_x00.N_2_5_MM: None,
                    self._nsb.fiber_x0020__implant6_x00.N_3_0_MM: None,
                    self._nsb.fiber_x0020__implant6_x00.N_3_5_MM: None,
                    self._nsb.fiber_x0020__implant6_x00.N_4_0_MM: None,
                    self._nsb.fiber_x0020__implant6_x00.N_4_5_MM: None,
                    self._nsb.fiber_x0020__implant6_x00.N_5_0_MM: None,
                }.get(self._nsb.fiber_x0020__implant6_x00, None)
            )
    
        @property
        def aind_fiber_x0020__implant6_x00_001(self) -> Optional[str]:
            """Maps fiber_x0020__implant6_x00_001 to aind model."""
            return self._nsb.fiber_x0020__implant6_x00_001

    @property
        def aind_burr3_x0020__status(self) -> Optional[Any]:
            """Maps burr3_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__status is None
                else {
                    self._nsb.burr3_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr3_x0020__status, None)
            )
    
        @property
        def aind_burr3_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr3_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__virus_x0020 is None
                else {
                    self._nsb.burr3_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr3_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr3_x0020_a_x002f_p to aind model."""
            return self._nsb.burr3_x0020_a_x002f_p

    @property
        def aind_burr6_x0020__status(self) -> Optional[Any]:
            """Maps burr6_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__status is None
                else {
                    self._nsb.burr6_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr6_x0020__status, None)
            )
    
        @property
        def aind_burr6_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr6_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__virus_x0020 is None
                else {
                    self._nsb.burr6_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr6_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_1_x0020__fiber.STANDARD_PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_1_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_1_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__grid(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__grid to aind model."""
            return self._nsb.burr_x0020_1_x0020__grid

    @property
        def aind_burr4_x0020_d_x002f_v(self) -> Optional[str]:
            """Maps burr4_x0020_d_x002f_v to aind model."""
            return self._nsb.burr4_x0020_d_x002f_v

    @property
        def aind_virus_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps virus_x0020_a_x002f_p to aind model."""
            return self._nsb.virus_x0020_a_x002f_p

    @property
        def aind_burr_x0020_1_x0020_dv_x00(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020_dv_x00 to aind model."""
            return self._nsb.burr_x0020_1_x0020_dv_x00

    @property
        def aind_burr4_x0020__status(self) -> Optional[Any]:
            """Maps burr4_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr4_x0020__status is None
                else {
                    self._nsb.burr4_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr4_x0020__status, None)
            )
    
        @property
        def aind_burr4_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr4_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr4_x0020__virus_x0020 is None
                else {
                    self._nsb.burr4_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr4_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr4_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr4_x0020_a_x002f_p to aind model."""
            return self._nsb.burr4_x0020_a_x002f_p

    @property
        def aind_burr5_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr5_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr5_x0020__injection_x0 is None
                else {
                    self._nsb.burr5_x0020__injection_x0.SELECT: None,
                    self._nsb.burr5_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr5_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr5_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr5_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr5_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr5_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr5_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr5_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr5_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr5_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr5_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr5_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr5_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr5_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr5_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr5_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr5_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr5_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr5_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr5_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr5_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr5_x0020__perform_x002 is None
                else {
                    self._nsb.burr5_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr5_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr5_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr5_x0020__status(self) -> Optional[Any]:
            """Maps burr5_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr5_x0020__status is None
                else {
                    self._nsb.burr5_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr5_x0020__status, None)
            )
    
        @property
        def aind_burr5_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr5_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr5_x0020__virus_x0020 is None
                else {
                    self._nsb.burr5_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr5_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr6_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr6_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__injection_x0 is None
                else {
                    self._nsb.burr6_x0020__injection_x0.SELECT: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr6_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr6_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr6_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__perform_x002 is None
                else {
                    self._nsb.burr6_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr6_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr6_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr6_x0020__status(self) -> Optional[Any]:
            """Maps burr6_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__status is None
                else {
                    self._nsb.burr6_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr6_x0020__status, None)
            )
    
        @property
        def aind_burr6_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr6_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__virus_x0020 is None
                else {
                    self._nsb.burr6_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr6_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_1_x0020__fiber.STANDARD_PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_1_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_1_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__grid(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__grid to aind model."""
            return self._nsb.burr_x0020_1_x0020__grid

    @property
        def aind_fiber_x0020__implant4_x00(self) -> Optional[Any]:
            """Maps fiber_x0020__implant4_x00 to aind model."""
            return (
                None
                if self._nsb.fiber_x0020__implant4_x00 is None
                else {
                    self._nsb.fiber_x0020__implant4_x00.SELECT: None,
                    self._nsb.fiber_x0020__implant4_x00.N_1_0_MM: None,
                    self._nsb.fiber_x0020__implant4_x00.N_1_5_MM: None,
                    self._nsb.fiber_x0020__implant4_x00.N_2_0_MM: None,
                    self._nsb.fiber_x0020__implant4_x00.N_2_5_MM: None,
                    self._nsb.fiber_x0020__implant4_x00.N_3_0_MM: None,
                    self._nsb.fiber_x0020__implant4_x00.N_3_5_MM: None,
                    self._nsb.fiber_x0020__implant4_x00.N_4_0_MM: None,
                    self._nsb.fiber_x0020__implant4_x00.N_4_5_MM: None,
                    self._nsb.fiber_x0020__implant4_x00.N_5_0_MM: None,
                }.get(self._nsb.fiber_x0020__implant4_x00, None)
            )
    
        @property
        def aind_fiber_x0020__implant4_x00_001(self) -> Optional[str]:
            """Maps fiber_x0020__implant4_x00_001 to aind model."""
            return self._nsb.fiber_x0020__implant4_x00_001

    @property
        def aind_burr_x0020_1_x0020__injec_002(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__injec_002 to aind model."""
            return self._nsb.burr_x0020_1_x0020__injec_002

    @property
        def aind_behavior_x0020__complete(self) -> Optional[str]:
            """Maps behavior_x0020__complete to aind model."""
            return self._nsb.behavior_x0020__complete

    @property
        def aind_burr_x0020_5_x0020_a_x002(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020_a_x002 to aind model."""
            return self._nsb.burr_x0020_5_x0020_a_x002

    @property
        def aind_burr4_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr4_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr4_x0020__perform_x002 is None
                else {
                    self._nsb.burr4_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr4_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr4_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr4_x0020__status(self) -> Optional[Any]:
            """Maps burr4_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr4_x0020__status is None
                else {
                    self._nsb.burr4_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr4_x0020__status, None)
            )
    
        @property
        def aind_burr4_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr4_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr4_x0020__virus_x0020 is None
                else {
                    self._nsb.burr4_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr4_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr4_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr4_x0020_a_x002f_p to aind model."""
            return self._nsb.burr4_x0020_a_x002f_p

    @property
        def aind_burr5_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr5_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr5_x0020__virus_x0020 is None
                else {
                    self._nsb.burr5_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr5_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr6_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr6_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__injection_x0 is None
                else {
                    self._nsb.burr6_x0020__injection_x0.SELECT: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr6_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr6_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr6_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__perform_x002 is None
                else {
                    self._nsb.burr6_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr6_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr6_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr6_x0020__status(self) -> Optional[Any]:
            """Maps burr6_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__status is None
                else {
                    self._nsb.burr6_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr6_x0020__status, None)
            )
    
        @property
        def aind_burr6_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr6_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__virus_x0020 is None
                else {
                    self._nsb.burr6_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr6_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_1_x0020__fiber.STANDARD_PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_1_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_1_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__grid(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__grid to aind model."""
            return self._nsb.burr_x0020_1_x0020__grid

    @property
        def aind_black_x0020__cement(self) -> Optional[Any]:
            """Maps black_x0020__cement to aind model."""
            return (
                None
                if self._nsb.black_x0020__cement is None
                else {
                    self._nsb.black_x0020__cement.YES: None,
                    self._nsb.black_x0020__cement.NO: None,
                }.get(self._nsb.black_x0020__cement, None)
            )
    
        @property
        def aind_breg2_lamb(self) -> Optional[str]:
            """Maps breg2_lamb to aind model."""
            return self._nsb.breg2_lamb

    @property
        def aind_fiber_x0020__implant1_x00(self) -> Optional[Any]:
            """Maps fiber_x0020__implant1_x00 to aind model."""
            return (
                None
                if self._nsb.fiber_x0020__implant1_x00 is None
                else {
                    self._nsb.fiber_x0020__implant1_x00.SELECT: None,
                    self._nsb.fiber_x0020__implant1_x00.N_1_0_MM: None,
                    self._nsb.fiber_x0020__implant1_x00.N_1_5_MM: None,
                    self._nsb.fiber_x0020__implant1_x00.N_2_0_MM: None,
                    self._nsb.fiber_x0020__implant1_x00.N_2_5_MM: None,
                    self._nsb.fiber_x0020__implant1_x00.N_3_0_MM: None,
                    self._nsb.fiber_x0020__implant1_x00.N_3_5_MM: None,
                    self._nsb.fiber_x0020__implant1_x00.N_4_0_MM: None,
                    self._nsb.fiber_x0020__implant1_x00.N_4_5_MM: None,
                    self._nsb.fiber_x0020__implant1_x00.N_5_0_MM: None,
                }.get(self._nsb.fiber_x0020__implant1_x00, None)
            )
    
        @property
        def aind_fiber_x0020__implant2_x00(self) -> Optional[Any]:
            """Maps fiber_x0020__implant2_x00 to aind model."""
            return (
                None
                if self._nsb.fiber_x0020__implant2_x00 is None
                else {
                    self._nsb.fiber_x0020__implant2_x00.SELECT: None,
                    self._nsb.fiber_x0020__implant2_x00.N_1_0_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_1_5_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_2_0_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_2_5_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_3_0_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_3_5_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_4_0_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_4_5_MM: None,
                    self._nsb.fiber_x0020__implant2_x00.N_5_0_MM: None,
                }.get(self._nsb.fiber_x0020__implant2_x00, None)
            )
    
        @property
        def aind_fiber_x0020__implant3_x00(self) -> Optional[Any]:
            """Maps fiber_x0020__implant3_x00 to aind model."""
            return (
                None
                if self._nsb.fiber_x0020__implant3_x00 is None
                else {
                    self._nsb.fiber_x0020__implant3_x00.SELECT: None,
                    self._nsb.fiber_x0020__implant3_x00.N_1_0_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_1_5_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_2_0_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_2_5_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_3_0_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_3_5_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_4_0_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_4_5_MM: None,
                    self._nsb.fiber_x0020__implant3_x00.N_5_0_MM: None,
                }.get(self._nsb.fiber_x0020__implant3_x00, None)
            )
    
        @property
        def aind_fiber_x0020__implant3_x00_001(self) -> Optional[str]:
            """Maps fiber_x0020__implant3_x00_001 to aind model."""
            return self._nsb.fiber_x0020__implant3_x00_001

    @property
        def aind_burr_x0020_hole_x0020_2(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_2 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_2 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_2.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_2.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_2.SPINAL__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_2.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_2.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_2, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_3(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_3 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_3 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_3.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_3.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_3.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_3.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_3, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_4(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_4 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_4 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_4.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_4.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_4.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_4.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_4, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_5(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_5 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_5 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_5.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_5.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_5.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_5.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_5, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_6(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_6 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_6 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_6.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_6.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_6.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_6.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_6, None)
            )
    
        @property
        def aind_care_x0020__moduele(self) -> Optional[Any]:
            """Maps care_x0020__moduele to aind model."""
            return (
                None
                if self._nsb.care_x0020__moduele is None
                else {
                    self._nsb.care_x0020__moduele.SELECT: None,
                    self._nsb.care_x0020__moduele.CM_S_01_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_01_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_03_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_03_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_04_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_04_C_D: None,
                }.get(self._nsb.care_x0020__moduele, None)
            )
    
        @property
        def aind_color_tag(self) -> Optional[str]:
            """Maps color_tag to aind model."""
            return self._nsb.color_tag

    @property
        def aind_burr_x0020_6_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_6_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_6_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_6_x0020__fiber.STANDARD_PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_6_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_6_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_6_x0020__hemis(self) -> Optional[Any]:
            """Maps burr_x0020_6_x0020__hemis to aind model."""
            return (
                None
                if self._nsb.burr_x0020_6_x0020__hemis is None
                else {
                    self._nsb.burr_x0020_6_x0020__hemis.SELECT: None,
                    self._nsb.burr_x0020_6_x0020__hemis.LEFT: None,
                    self._nsb.burr_x0020_6_x0020__hemis.RIGHT: None,
                }.get(self._nsb.burr_x0020_6_x0020__hemis, None)
            )
    
        @property
        def aind_burr_x0020_6_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020__injec to aind model."""
            return self._nsb.burr_x0020_6_x0020__injec

    @property
        def aind_burr_x0020_2_x0020_d_x002_001(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020_d_x002_001 to aind model."""
            return self._nsb.burr_x0020_2_x0020_d_x002_001

    @property
        def aind_burr_x0020_3_x0020__inten(self) -> Optional[Any]:
            """Maps burr_x0020_3_x0020__inten to aind model."""
            return (
                None
                if self._nsb.burr_x0020_3_x0020__inten is None
                else {
                    self._nsb.burr_x0020_3_x0020__inten.FRP__FRONTAL_POLE_CEREBRA: None,
                    self._nsb.burr_x0020_3_x0020__inten.M_OP__PRIMARY_MOTOR_AREA: None,
                    self._nsb.burr_x0020_3_x0020__inten.M_OS__SECONDARY_MOTOR_ARE: None,
                    self._nsb.burr_x0020_3_x0020__inten.S_SP_N__PRIMARY_SOMATOSEN: None,
                    self._nsb.burr_x0020_3_x0020__inten.S_SP_BFD__PRIMARY_SOMATOS: None,
                    self._nsb.burr_x0020_3_x0020__inten.S_SP_LL__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_3_x0020__inten.S_SP_M__PRIMARY_SOMATOSEN: None,
                    self._nsb.burr_x0020_3_x0020__inten.S_SP_UL__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_3_x0020__inten.S_SP_TR__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_3_x0020__inten.S_SP_UN__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_3_x0020__inten.S_SS__SUPPLEMENTAL_SOMATO: None,
                    self._nsb.burr_x0020_3_x0020__inten.GU__GUSTATORY_AREAS: None,
                    self._nsb.burr_x0020_3_x0020__inten.VISC__VISCERAL_AREA: None,
                    self._nsb.burr_x0020_3_x0020__inten.AU_DD__DORSAL_AUDITORY_AR: None,
                    self._nsb.burr_x0020_3_x0020__inten.AU_DP__PRIMARY_AUDITORY_A: None,
                    self._nsb.burr_x0020_3_x0020__inten.AU_DPO__POSTERIOR_AUDITOR: None,
                    self._nsb.burr_x0020_3_x0020__inten.AU_DV__VENTRAL_AUDITORY_A: None,
                    self._nsb.burr_x0020_3_x0020__inten.VI_SAL__ANTEROLATERAL_VIS: None,
                    self._nsb.burr_x0020_3_x0020__inten.VI_SAM__ANTEROMEDIAL_VISU: None,
                    self._nsb.burr_x0020_3_x0020__inten.VI_SL__LATERAL_VISUAL_ARE: None,
                    self._nsb.burr_x0020_3_x0020__inten.VI_SP__PRIMARY_VISUAL_ARE: None,
                    self._nsb.burr_x0020_3_x0020__inten.VI_SPL__POSTEROLATERAL_VI: None,
                    self._nsb.burr_x0020_3_x0020__inten.VI_SPM_POSTEROMEDIAL_VISU: None,
                    self._nsb.burr_x0020_3_x0020__inten.VI_SLI__LATEROINTERMEDIAT: None,
                    self._nsb.burr_x0020_3_x0020__inten.VI_SPOR__POSTRHINAL_AREA: None,
                    self._nsb.burr_x0020_3_x0020__inten.AC_AD__ANTERIOR_CINGULATE: None,
                    self._nsb.burr_x0020_3_x0020__inten.AC_AV__ANTERIOR_CINGULATE: None,
                    self._nsb.burr_x0020_3_x0020__inten.PL__PRELIMBIC_AREA: None,
                    self._nsb.burr_x0020_3_x0020__inten.ILA__INFRALIMBIC_AREA: None,
                    self._nsb.burr_x0020_3_x0020__inten.OR_BL__ORBITAL_AREA_LATER: None,
                    self._nsb.burr_x0020_3_x0020__inten.OR_BM__ORBITAL_AREA_MEDIA: None,
                    self._nsb.burr_x0020_3_x0020__inten.OR_BV__ORBITAL_AREA_VENTR: None,
                    self._nsb.burr_x0020_3_x0020__inten.OR_BVL__ORBITAL_AREA_VENT: None,
                    self._nsb.burr_x0020_3_x0020__inten.A_ID__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_3_x0020__inten.A_IP__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_3_x0020__inten.A_IV__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_3_x0020__inten.RS_PAGL__RETROSPLENIAL_AR: None,
                    self._nsb.burr_x0020_3_x0020__inten.RS_PD__RETROSPLENIAL_AREA: None,
                    self._nsb.burr_x0020_3_x0020__inten.RS_PV__RETROSPLENIAL_AREA: None,
                    self._nsb.burr_x0020_3_x0020__inten.VI_SA__ANTERIOR_AREA: None,
                    self._nsb.burr_x0020_3_x0020__inten.VI_SRL__ROSTROLATERAL_VIS: None,
                    self._nsb.burr_x0020_3_x0020__inten.T_EA__TEMPORAL_ASSOCIATIO: None,
                    self._nsb.burr_x0020_3_x0020__inten.PERI__PERIRHINAL_AREA: None,
                    self._nsb.burr_x0020_3_x0020__inten.ECT__ECTORHINAL_AREA: None,
                    self._nsb.burr_x0020_3_x0020__inten.MOB__MAIN_OLFACTORY_BULB: None,
                    self._nsb.burr_x0020_3_x0020__inten.AOB__ACCESSORY_OLFACTORY: None,
                    self._nsb.burr_x0020_3_x0020__inten.AON__ANTERIOR_OLFACTORY_N: None,
                    self._nsb.burr_x0020_3_x0020__inten.T_TD__TAENIA_TECTA_DORSAL: None,
                    self._nsb.burr_x0020_3_x0020__inten.T_TV__TAENIA_TECTA_VENTRA: None,
                    self._nsb.burr_x0020_3_x0020__inten.DP__DORSAL_PEDUNCULAR_ARE: None,
                    self._nsb.burr_x0020_3_x0020__inten.PIR__PIRIFORM_AREA: None,
                    self._nsb.burr_x0020_3_x0020__inten.NLOT__NUCLEUS_OF_THE_LATE: None,
                    self._nsb.burr_x0020_3_x0020__inten.CO_AA__CORTICAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_3_x0020__inten.CO_AP__CORTICAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_3_x0020__inten.PAA__PIRIFORM_AMYGDALAR_A: None,
                    self._nsb.burr_x0020_3_x0020__inten.TR__POSTPIRIFORM_TRANSITI: None,
                    self._nsb.burr_x0020_3_x0020__inten.CA1__FIELD_CA1: None,
                    self._nsb.burr_x0020_3_x0020__inten.CA2__FIELD_CA2: None,
                    self._nsb.burr_x0020_3_x0020__inten.CA3__FIELD_CA3: None,
                    self._nsb.burr_x0020_3_x0020__inten.DG__DENTATE_GYRUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.FC__FASCIOLA_CINEREA: None,
                    self._nsb.burr_x0020_3_x0020__inten.IG__INDUSEUM_GRISEUM: None,
                    self._nsb.burr_x0020_3_x0020__inten.EN_TL__ENTORHINAL_AREA_LA: None,
                    self._nsb.burr_x0020_3_x0020__inten.EN_TM__ENTORHINAL_AREA_ME: None,
                    self._nsb.burr_x0020_3_x0020__inten.PAR__PARASUBICULUM: None,
                    self._nsb.burr_x0020_3_x0020__inten.POST__POSTSUBICULUM: None,
                    self._nsb.burr_x0020_3_x0020__inten.PRE__PRESUBICULUM: None,
                    self._nsb.burr_x0020_3_x0020__inten.SUB__SUBICULUM: None,
                    self._nsb.burr_x0020_3_x0020__inten.PRO_S__PROSUBICULUM: None,
                    self._nsb.burr_x0020_3_x0020__inten.HATA__HIPPOCAMPO_AMYGDALA: None,
                    self._nsb.burr_x0020_3_x0020__inten.A_PR__AREA_PROSTRIATA: None,
                    self._nsb.burr_x0020_3_x0020__inten.CLA__CLAUSTRUM: None,
                    self._nsb.burr_x0020_3_x0020__inten.E_PD__ENDOPIRIFORM_NUCLEU: None,
                    self._nsb.burr_x0020_3_x0020__inten.E_PV__ENDOPIRIFORM_NUCLEU: None,
                    self._nsb.burr_x0020_3_x0020__inten.LA__LATERAL_AMYGDALAR_NUC: None,
                    self._nsb.burr_x0020_3_x0020__inten.BLA__BASOLATERAL_AMYGDALA: None,
                    self._nsb.burr_x0020_3_x0020__inten.BMA__BASOMEDIAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_3_x0020__inten.PA__POSTERIOR_AMYGDALAR_N: None,
                    self._nsb.burr_x0020_3_x0020__inten.CP__CAUDOPUTAMEN: None,
                    self._nsb.burr_x0020_3_x0020__inten.ACB__NUCLEUS_ACCUMBENS: None,
                    self._nsb.burr_x0020_3_x0020__inten.FS__FUNDUS_OF_STRIATUM: None,
                    self._nsb.burr_x0020_3_x0020__inten.OT__OLFACTORY_TUBERCLE: None,
                    self._nsb.burr_x0020_3_x0020__inten.L_SC__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.L_SR__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.L_SV__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.SF__SEPTOFIMBRIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.SH__SEPTOHIPPOCAMPAL_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.AAA__ANTERIOR_AMYGDALAR_A: None,
                    self._nsb.burr_x0020_3_x0020__inten.BA__BED_NUCLEUS_OF_THE_AC: None,
                    self._nsb.burr_x0020_3_x0020__inten.CEA__CENTRAL_AMYGDALAR_NU: None,
                    self._nsb.burr_x0020_3_x0020__inten.IA__INTERCALATED_AMYGDALA: None,
                    self._nsb.burr_x0020_3_x0020__inten.MEA__MEDIAL_AMYGDALAR_NUC: None,
                    self._nsb.burr_x0020_3_x0020__inten.G_PE__GLOBUS_PALLIDUS_EXT: None,
                    self._nsb.burr_x0020_3_x0020__inten.G_PI__GLOBUS_PALLIDUS_INT: None,
                    self._nsb.burr_x0020_3_x0020__inten.SI__SUBSTANTIA_INNOMINATA: None,
                    self._nsb.burr_x0020_3_x0020__inten.MA__MAGNOCELLULAR_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.MS__MEDIAL_SEPTAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.NDB__DIAGONAL_BAND_NUCLEU: None,
                    self._nsb.burr_x0020_3_x0020__inten.TRS__TRIANGULAR_NUCLEUS_O: None,
                    self._nsb.burr_x0020_3_x0020__inten.BST__BED_NUCLEI_OF_THE_ST: None,
                    self._nsb.burr_x0020_3_x0020__inten.VAL__VENTRAL_ANTERIOR_LAT: None,
                    self._nsb.burr_x0020_3_x0020__inten.VM__VENTRAL_MEDIAL_NUCLEU: None,
                    self._nsb.burr_x0020_3_x0020__inten.VPL__VENTRAL_POSTEROLATER: None,
                    self._nsb.burr_x0020_3_x0020__inten.VP_LPC__VENTRAL_POSTEROLA: None,
                    self._nsb.burr_x0020_3_x0020__inten.VPM__VENTRAL_POSTEROMEDIA: None,
                    self._nsb.burr_x0020_3_x0020__inten.VP_MPC__VENTRAL_POSTEROME: None,
                    self._nsb.burr_x0020_3_x0020__inten.PO_T__POSTERIOR_TRIANGULA: None,
                    self._nsb.burr_x0020_3_x0020__inten.SPF__SUBPARAFASCICULAR_NU: None,
                    self._nsb.burr_x0020_3_x0020__inten.SPA__SUBPARAFASCICULAR_AR: None,
                    self._nsb.burr_x0020_3_x0020__inten.PP__PERIPEDUNCULAR_NUCLEU: None,
                    self._nsb.burr_x0020_3_x0020__inten.MG__MEDIAL_GENICULATE_COM: None,
                    self._nsb.burr_x0020_3_x0020__inten.L_GD__DORSAL_PART_OF_THE: None,
                    self._nsb.burr_x0020_3_x0020__inten.LP__LATERAL_POSTERIOR_NUC: None,
                    self._nsb.burr_x0020_3_x0020__inten.PO__POSTERIOR_COMPLEX_OF: None,
                    self._nsb.burr_x0020_3_x0020__inten.POL__POSTERIOR_LIMITING_N: None,
                    self._nsb.burr_x0020_3_x0020__inten.SGN__SUPRAGENICULATE_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.ETH__ETHMOID_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_3_x0020__inten.AV__ANTEROVENTRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.AM__ANTEROMEDIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.AD__ANTERODORSAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.IAM__INTERANTEROMEDIAL_NU: None,
                    self._nsb.burr_x0020_3_x0020__inten.IAD__INTERANTERODORSAL_NU: None,
                    self._nsb.burr_x0020_3_x0020__inten.LD__LATERAL_DORSAL_NUCLEU: None,
                    self._nsb.burr_x0020_3_x0020__inten.IMD__INTERMEDIODORSAL_NUC: None,
                    self._nsb.burr_x0020_3_x0020__inten.MD__MEDIODORSAL_NUCLEUS_O: None,
                    self._nsb.burr_x0020_3_x0020__inten.SMT__SUBMEDIAL_NUCLEUS_OF: None,
                    self._nsb.burr_x0020_3_x0020__inten.PR__PERIREUNENSIS_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.PVT__PARAVENTRICULAR_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.PT__PARATAENIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.RE__NUCLEUS_OF_REUNIENS: None,
                    self._nsb.burr_x0020_3_x0020__inten.XI__XIPHOID_THALAMIC_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.RH__RHOMBOID_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.CM__CENTRAL_MEDIAL_NUCLEU: None,
                    self._nsb.burr_x0020_3_x0020__inten.PCN__PARACENTRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.CL__CENTRAL_LATERAL_NUCLE: None,
                    self._nsb.burr_x0020_3_x0020__inten.PF__PARAFASCICULAR_NUCLEU: None,
                    self._nsb.burr_x0020_3_x0020__inten.PIL__POSTERIOR_INTRALAMIN: None,
                    self._nsb.burr_x0020_3_x0020__inten.RT__RETICULAR_NUCLEUS_OF: None,
                    self._nsb.burr_x0020_3_x0020__inten.IGL__INTERGENICULATE_LEAF: None,
                    self._nsb.burr_x0020_3_x0020__inten.INT_G__INTERMEDIATE_GENIC: None,
                    self._nsb.burr_x0020_3_x0020__inten.L_GV__VENTRAL_PART_OF_THE: None,
                    self._nsb.burr_x0020_3_x0020__inten.SUB_G__SUBGENICULATE_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.MH__MEDIAL_HABENULA: None,
                    self._nsb.burr_x0020_3_x0020__inten.LH__LATERAL_HABENULA: None,
                    self._nsb.burr_x0020_3_x0020__inten.SO__SUPRAOPTIC_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.PVH__PARAVENTRICULAR_HYPO: None,
                    self._nsb.burr_x0020_3_x0020__inten.P_VA__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_3_x0020__inten.P_VI__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_3_x0020__inten.ARH__ARCUATE_HYPOTHALAMIC: None,
                    self._nsb.burr_x0020_3_x0020__inten.ADP__ANTERODORSAL_PREOPTI: None,
                    self._nsb.burr_x0020_3_x0020__inten.AVP__ANTEROVENTRAL_PREOPT: None,
                    self._nsb.burr_x0020_3_x0020__inten.AVPV__ANTEROVENTRAL_PERIV: None,
                    self._nsb.burr_x0020_3_x0020__inten.DMH__DORSOMEDIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.MEPO__MEDIAN_PREOPTIC_NUC: None,
                    self._nsb.burr_x0020_3_x0020__inten.MPO__MEDIAL_PREOPTIC_AREA: None,
                    self._nsb.burr_x0020_3_x0020__inten.PS__PARASTRIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.P_VP__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_3_x0020__inten.P_VPO__PERIVENTRICULAR_HY: None,
                    self._nsb.burr_x0020_3_x0020__inten.SBPV__SUBPARAVENTRICULAR: None,
                    self._nsb.burr_x0020_3_x0020__inten.SCH__SUPRACHIASMATIC_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.SFO__SUBFORNICAL_ORGAN: None,
                    self._nsb.burr_x0020_3_x0020__inten.VMPO__VENTROMEDIAL_PREOPT: None,
                    self._nsb.burr_x0020_3_x0020__inten.VLPO__VENTROLATERAL_PREOP: None,
                    self._nsb.burr_x0020_3_x0020__inten.AHN__ANTERIOR_HYPOTHALAMI: None,
                    self._nsb.burr_x0020_3_x0020__inten.LM__LATERAL_MAMMILLARY_NU: None,
                    self._nsb.burr_x0020_3_x0020__inten.MM__MEDIAL_MAMMILLARY_NUC: None,
                    self._nsb.burr_x0020_3_x0020__inten.SUM__SUPRAMAMMILLARY_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.TM__TUBEROMAMMILLARY_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.MPN__MEDIAL_PREOPTIC_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.P_MD__DORSAL_PREMAMMILLAR: None,
                    self._nsb.burr_x0020_3_x0020__inten.P_MV__VENTRAL_PREMAMMILLA: None,
                    self._nsb.burr_x0020_3_x0020__inten.PV_HD__PARAVENTRICULAR_HY: None,
                    self._nsb.burr_x0020_3_x0020__inten.VMH__VENTROMEDIAL_HYPOTHA: None,
                    self._nsb.burr_x0020_3_x0020__inten.PH__POSTERIOR_HYPOTHALAMI: None,
                    self._nsb.burr_x0020_3_x0020__inten.LHA__LATERAL_HYPOTHALAMIC: None,
                    self._nsb.burr_x0020_3_x0020__inten.LPO__LATERAL_PREOPTIC_ARE: None,
                    self._nsb.burr_x0020_3_x0020__inten.PSTN__PARASUBTHALAMIC_NUC: None,
                    self._nsb.burr_x0020_3_x0020__inten.PE_F__PERIFORNICAL_NUCLEU: None,
                    self._nsb.burr_x0020_3_x0020__inten.RCH__RETROCHIASMATIC_AREA: None,
                    self._nsb.burr_x0020_3_x0020__inten.STN__SUBTHALAMIC_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.TU__TUBERAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.ZI__ZONA_INCERTA: None,
                    self._nsb.burr_x0020_3_x0020__inten.S_CS__SUPERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.IC__INFERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.NB__NUCLEUS_OF_THE_BRACHI: None,
                    self._nsb.burr_x0020_3_x0020__inten.SAG__NUCLEUS_SAGULUM: None,
                    self._nsb.burr_x0020_3_x0020__inten.PBG__PARABIGEMINAL_NUCLEU: None,
                    self._nsb.burr_x0020_3_x0020__inten.S_NR__SUBSTANTIA_NIGRA_RE: None,
                    self._nsb.burr_x0020_3_x0020__inten.VTA__VENTRAL_TEGMENTAL_AR: None,
                    self._nsb.burr_x0020_3_x0020__inten.PN__PARANIGRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.RR__MIDBRAIN_RETICULAR_NU: None,
                    self._nsb.burr_x0020_3_x0020__inten.MRN__MIDBRAIN_RETICULAR_N: None,
                    self._nsb.burr_x0020_3_x0020__inten.S_CM__SUPERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.PAG__PERIAQUEDUCTAL_GRAY: None,
                    self._nsb.burr_x0020_3_x0020__inten.APN__ANTERIOR_PRETECTAL_N: None,
                    self._nsb.burr_x0020_3_x0020__inten.MPT__MEDIAL_PRETECTAL_ARE: None,
                    self._nsb.burr_x0020_3_x0020__inten.NOT__NUCLEUS_OF_THE_OPTIC: None,
                    self._nsb.burr_x0020_3_x0020__inten.NPC__NUCLEUS_OF_THE_POSTE: None,
                    self._nsb.burr_x0020_3_x0020__inten.OP__OLIVARY_PRETECTAL_NUC: None,
                    self._nsb.burr_x0020_3_x0020__inten.PPT__POSTERIOR_PRETECTAL: None,
                    self._nsb.burr_x0020_3_x0020__inten.RPF__RETROPARAFASCICULAR: None,
                    self._nsb.burr_x0020_3_x0020__inten.CUN__CUNEIFORM_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.RN__RED_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.III__OCULOMOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.MA3__MEDIAL_ACCESORY_OCUL: None,
                    self._nsb.burr_x0020_3_x0020__inten.EW__EDINGER__WESTPHAL_NUC: None,
                    self._nsb.burr_x0020_3_x0020__inten.IV__TROCHLEAR_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.PA4__PARATROCHLEAR_NUCLEU: None,
                    self._nsb.burr_x0020_3_x0020__inten.VTN__VENTRAL_TEGMENTAL_NU: None,
                    self._nsb.burr_x0020_3_x0020__inten.AT__ANTERIOR_TEGMENTAL_NU: None,
                    self._nsb.burr_x0020_3_x0020__inten.LT__LATERAL_TERMINAL_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.DT__DORSAL_TERMINAL_NUCLE: None,
                    self._nsb.burr_x0020_3_x0020__inten.MT__MEDIAL_TERMINAL_NUCLE: None,
                    self._nsb.burr_x0020_3_x0020__inten.S_NC__SUBSTANTIA_NIGRA_CO: None,
                    self._nsb.burr_x0020_3_x0020__inten.PPN__PEDUNCULOPONTINE_NUC: None,
                    self._nsb.burr_x0020_3_x0020__inten.IF__INTERFASCICULAR_NUCLE: None,
                    self._nsb.burr_x0020_3_x0020__inten.IPN__INTERPEDUNCULAR_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.RL__ROSTRAL_LINEAR_NUCLEU: None,
                    self._nsb.burr_x0020_3_x0020__inten.CLI__CENTRAL_LINEAR_NUCLE: None,
                    self._nsb.burr_x0020_3_x0020__inten.DR__DORSAL_NUCLEUS_RAPHE: None,
                    self._nsb.burr_x0020_3_x0020__inten.NLL__NUCLEUS_OF_THE_LATER: None,
                    self._nsb.burr_x0020_3_x0020__inten.PSV__PRINCIPAL_SENSORY_NU: None,
                    self._nsb.burr_x0020_3_x0020__inten.PB__PARABRACHIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.SOC__SUPERIOR_OLIVARY_COM: None,
                    self._nsb.burr_x0020_3_x0020__inten.B__BARRINGTON_S_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.DTN__DORSAL_TEGMENTAL_NUC: None,
                    self._nsb.burr_x0020_3_x0020__inten.PD_TG__POSTERODORSAL_TEGM: None,
                    self._nsb.burr_x0020_3_x0020__inten.PCG__PONTINE_CENTRAL_GRAY: None,
                    self._nsb.burr_x0020_3_x0020__inten.PG__PONTINE_GRAY: None,
                    self._nsb.burr_x0020_3_x0020__inten.PR_NC__PONTINE_RETICULAR: None,
                    self._nsb.burr_x0020_3_x0020__inten.SG__SUPRAGENUAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.SUT__SUPRATRIGEMINAL_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.TRN__TEGMENTAL_RETICULAR: None,
                    self._nsb.burr_x0020_3_x0020__inten.V__MOTOR_NUCLEUS_OF_TRIGE: None,
                    self._nsb.burr_x0020_3_x0020__inten.P5__PERITRIGEMINAL_ZONE: None,
                    self._nsb.burr_x0020_3_x0020__inten.ACS5__ACCESSORY_TRIGEMINA: None,
                    self._nsb.burr_x0020_3_x0020__inten.PC5__PARVICELLULAR_MOTOR: None,
                    self._nsb.burr_x0020_3_x0020__inten.I5__INTERTRIGEMINAL_NUCLE: None,
                    self._nsb.burr_x0020_3_x0020__inten.CS__SUPERIOR_CENTRAL_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.LC__LOCUS_CERULEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.LDT__LATERODORSAL_TEGMENT: None,
                    self._nsb.burr_x0020_3_x0020__inten.NI__NUCLEUS_INCERTUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.PR_NR__PONTINE_RETICULAR: None,
                    self._nsb.burr_x0020_3_x0020__inten.RPO__NUCLEUS_RAPHE_PONTIS: None,
                    self._nsb.burr_x0020_3_x0020__inten.SLC__SUBCERULEUS_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.SLD__SUBLATERODORSAL_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.MY__MEDULLA: None,
                    self._nsb.burr_x0020_3_x0020__inten.AP__AREA_POSTREMA: None,
                    self._nsb.burr_x0020_3_x0020__inten.DCO__DORSAL_COCHLEAR_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.VCO__VENTRAL_COCHLEAR_NUC: None,
                    self._nsb.burr_x0020_3_x0020__inten.CU__CUNEATE_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.GR__GRACILE_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.ECU__EXTERNAL_CUNEATE_NUC: None,
                    self._nsb.burr_x0020_3_x0020__inten.NTB__NUCLEUS_OF_THE_TRAPE: None,
                    self._nsb.burr_x0020_3_x0020__inten.NTS__NUCLEUS_OF_THE_SOLIT: None,
                    self._nsb.burr_x0020_3_x0020__inten.SPVC__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_3_x0020__inten.SPVI__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_3_x0020__inten.SPVO__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_3_x0020__inten.PA5__PARATRIGEMINAL_NUCLE: None,
                    self._nsb.burr_x0020_3_x0020__inten.VI__ABDUCENS_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.VII__FACIAL_MOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.AMB__NUCLEUS_AMBIGUUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.DMX__DORSAL_MOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.GRN__GIGANTOCELLULAR_RETI: None,
                    self._nsb.burr_x0020_3_x0020__inten.ICB__INFRACEREBELLAR_NUCL: None,
                    self._nsb.burr_x0020_3_x0020__inten.IO__INFERIOR_OLIVARY_COMP: None,
                    self._nsb.burr_x0020_3_x0020__inten.IRN__INTERMEDIATE_RETICUL: None,
                    self._nsb.burr_x0020_3_x0020__inten.ISN__INFERIOR_SALIVATORY: None,
                    self._nsb.burr_x0020_3_x0020__inten.LIN__LINEAR_NUCLEUS_OF_TH: None,
                    self._nsb.burr_x0020_3_x0020__inten.LRN__LATERAL_RETICULAR_NU: None,
                    self._nsb.burr_x0020_3_x0020__inten.MARN__MAGNOCELLULAR_RETIC: None,
                    self._nsb.burr_x0020_3_x0020__inten.MDRN__MEDULLARY_RETICULAR: None,
                    self._nsb.burr_x0020_3_x0020__inten.PARN__PARVICELLULAR_RETIC: None,
                    self._nsb.burr_x0020_3_x0020__inten.PAS__PARASOLITARY_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.PGRN__PARAGIGANTOCELLULAR: None,
                    self._nsb.burr_x0020_3_x0020__inten.NR__NUCLEUS_OF__ROLLER: None,
                    self._nsb.burr_x0020_3_x0020__inten.PRP__NUCLEUS_PREPOSITUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.PMR__PARAMEDIAN_RETICULAR: None,
                    self._nsb.burr_x0020_3_x0020__inten.PPY__PARAPYRAMIDAL_NUCLEU: None,
                    self._nsb.burr_x0020_3_x0020__inten.LAV__LATERAL_VESTIBULAR_N: None,
                    self._nsb.burr_x0020_3_x0020__inten.MV__MEDIAL_VESTIBULAR_NUC: None,
                    self._nsb.burr_x0020_3_x0020__inten.SPIV__SPINAL_VESTIBULAR_N: None,
                    self._nsb.burr_x0020_3_x0020__inten.SUV__SUPERIOR_VESTIBULAR: None,
                    self._nsb.burr_x0020_3_x0020__inten.X__NUCLEUS_X: None,
                    self._nsb.burr_x0020_3_x0020__inten.XII__HYPOGLOSSAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.Y__NUCLEUS_Y: None,
                    self._nsb.burr_x0020_3_x0020__inten.RM__NUCLEUS_RAPHE_MAGNUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.RPA__NUCLEUS_RAPHE_PALLID: None,
                    self._nsb.burr_x0020_3_x0020__inten.RO__NUCLEUS_RAPHE_OBSCURU: None,
                    self._nsb.burr_x0020_3_x0020__inten.LING__LINGULA_I: None,
                    self._nsb.burr_x0020_3_x0020__inten.CENT2__LOBULE_II: None,
                    self._nsb.burr_x0020_3_x0020__inten.CENT3__LOBULE_III: None,
                    self._nsb.burr_x0020_3_x0020__inten.CUL4_5__LOBULES_IV_V: None,
                    self._nsb.burr_x0020_3_x0020__inten.DEC__DECLIVE_VI: None,
                    self._nsb.burr_x0020_3_x0020__inten.FOTU__FOLIUM_TUBER_VERMIS: None,
                    self._nsb.burr_x0020_3_x0020__inten.PYR__PYRAMUS_VIII: None,
                    self._nsb.burr_x0020_3_x0020__inten.UVU__UVULA_IX: None,
                    self._nsb.burr_x0020_3_x0020__inten.NOD__NODULUS_X: None,
                    self._nsb.burr_x0020_3_x0020__inten.SIM__SIMPLE_LOBULE: None,
                    self._nsb.burr_x0020_3_x0020__inten.A_NCR1__CRUS_1: None,
                    self._nsb.burr_x0020_3_x0020__inten.A_NCR2__CRUS_2: None,
                    self._nsb.burr_x0020_3_x0020__inten.PRM__PARAMEDIAN_LOBULE: None,
                    self._nsb.burr_x0020_3_x0020__inten.COPY__COPULA_PYRAMIDIS: None,
                    self._nsb.burr_x0020_3_x0020__inten.PFL__PARAFLOCCULUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.FL__FLOCCULUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.FN__FASTIGIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.IP__INTERPOSED_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.DN__DENTATE_NUCLEUS: None,
                    self._nsb.burr_x0020_3_x0020__inten.VE_CB__VESTIBULOCEREBELLA: None,
                }.get(self._nsb.burr_x0020_3_x0020__inten, None)
            )
    
        @property
        def aind_burr_x0020_3_x0020_d_x002(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020_d_x002 to aind model."""
            return self._nsb.burr_x0020_3_x0020_d_x002

    @property
        def aind_author(self) -> Optional[str]:
            """Maps author to aind model."""
            return self._nsb.author

    @property
        def aind_burr_x0020_3_x0020__hemis(self) -> Optional[Any]:
            """Maps burr_x0020_3_x0020__hemis to aind model."""
            return (
                None
                if self._nsb.burr_x0020_3_x0020__hemis is None
                else {
                    self._nsb.burr_x0020_3_x0020__hemis.SELECT: None,
                    self._nsb.burr_x0020_3_x0020__hemis.LEFT: None,
                    self._nsb.burr_x0020_3_x0020__hemis.RIGHT: None,
                }.get(self._nsb.burr_x0020_3_x0020__hemis, None)
            )
    
        @property
        def aind_burr_x0020_3_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__injec to aind model."""
            return self._nsb.burr_x0020_3_x0020__injec

    @property
        def aind_burr_x0020_3_x0020_intend_001(self) -> Optional[Any]:
            """Maps burr_x0020_3_x0020_intend_001 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_3_x0020_intend_001 is None
                else {
                    self._nsb.burr_x0020_3_x0020_intend_001.N_A: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.DOPAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.SEROTONIN: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.HISTAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.GLUTAMATE: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.GABA: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.CALCIUM: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.VOLTAGE: None,
                    self._nsb.burr_x0020_3_x0020_intend_001.CONTROL: None,
                }.get(self._nsb.burr_x0020_3_x0020_intend_001, None)
            )
    
        @property
        def aind_burr_x0020_3_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_3_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_3_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_3_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_3_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_3_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_3_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_3_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_3_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_3_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_3_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_3_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_4_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__angle to aind model."""
            return self._nsb.burr_x0020_4_x0020__angle

    @property
        def aind_iacuc_x0020__protocol_x00(self) -> Optional[Any]:
            """Maps iacuc_x0020__protocol_x00 to aind model."""
            return (
                None
                if self._nsb.iacuc_x0020__protocol_x00 is None
                else {
                    self._nsb.iacuc_x0020__protocol_x00.SELECT: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2117: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2201: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2202: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2205: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2212: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2301: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2304: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2305: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2306: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2307: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2401: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2402: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2403: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2404: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2405: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2406: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2410: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2412: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2413: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2414: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2415: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2416: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2418: None,
                    self._nsb.iacuc_x0020__protocol_x00.N_2427: None,
                }.get(self._nsb.iacuc_x0020__protocol_x00, None)
            )
    
        @property
        def aind_id(self) -> Optional[str]:
            """Maps id to aind model."""
            return self._nsb.id

    @property
        def aind_fiber_x0020__implant5_x00(self) -> Optional[Any]:
            """Maps fiber_x0020__implant5_x00 to aind model."""
            return (
                None
                if self._nsb.fiber_x0020__implant5_x00 is None
                else {
                    self._nsb.fiber_x0020__implant5_x00.SELECT: None,
                    self._nsb.fiber_x0020__implant5_x00.N_1_0_MM: None,
                    self._nsb.fiber_x0020__implant5_x00.N_1_5_MM: None,
                    self._nsb.fiber_x0020__implant5_x00.N_2_0_MM: None,
                    self._nsb.fiber_x0020__implant5_x00.N_2_5_MM: None,
                    self._nsb.fiber_x0020__implant5_x00.N_3_0_MM: None,
                    self._nsb.fiber_x0020__implant5_x00.N_3_5_MM: None,
                    self._nsb.fiber_x0020__implant5_x00.N_4_0_MM: None,
                    self._nsb.fiber_x0020__implant5_x00.N_4_5_MM: None,
                    self._nsb.fiber_x0020__implant5_x00.N_5_0_MM: None,
                }.get(self._nsb.fiber_x0020__implant5_x00, None)
            )
    
        @property
        def aind_fiber_x0020__implant5_x00_001(self) -> Optional[str]:
            """Maps fiber_x0020__implant5_x00_001 to aind model."""
            return self._nsb.fiber_x0020__implant5_x00_001

    @property
        def aind_burr_x0020_6_x0020_intend(self) -> Optional[Any]:
            """Maps burr_x0020_6_x0020_intend to aind model."""
            return (
                None
                if self._nsb.burr_x0020_6_x0020_intend is None
                else {
                    self._nsb.burr_x0020_6_x0020_intend.N_A: None,
                    self._nsb.burr_x0020_6_x0020_intend.DOPAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend.SEROTONIN: None,
                    self._nsb.burr_x0020_6_x0020_intend.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_6_x0020_intend.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_6_x0020_intend.HISTAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend.GLUTAMATE: None,
                    self._nsb.burr_x0020_6_x0020_intend.GABA: None,
                    self._nsb.burr_x0020_6_x0020_intend.CALCIUM: None,
                    self._nsb.burr_x0020_6_x0020_intend.VOLTAGE: None,
                    self._nsb.burr_x0020_6_x0020_intend.CONTROL: None,
                }.get(self._nsb.burr_x0020_6_x0020_intend, None)
            )
    
        @property
        def aind_burr_x0020_6_x0020_intend_001(self) -> Optional[Any]:
            """Maps burr_x0020_6_x0020_intend_001 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_6_x0020_intend_001 is None
                else {
                    self._nsb.burr_x0020_6_x0020_intend_001.N_A: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.DOPAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.SEROTONIN: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.HISTAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.GLUTAMATE: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.GABA: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.CALCIUM: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.VOLTAGE: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.CONTROL: None,
                }.get(self._nsb.burr_x0020_6_x0020_intend_001, None)
            )
    
        @property
        def aind_burr_x0020_6_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_6_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_6_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_6_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_6_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_6_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_6_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_6_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_6_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_6_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_6_x0020_m_x002(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020_m_x002 to aind model."""
            return self._nsb.burr_x0020_6_x0020_m_x002

    @property
        def aind_thermistor(self) -> Optional[Any]:
            """Maps thermistor to aind model."""
            return (
                None
                if self._nsb.thermistor is None
                else {
                    self._nsb.thermistor.NO: None,
                    self._nsb.thermistor.YES: None,
                }.get(self._nsb.thermistor, None)
            )
    
        @property
        def aind_title(self) -> Optional[str]:
            """Maps title to aind model."""
            return self._nsb.title

    @property
        def aind_virus_x0020__hemisphere(self) -> Optional[Any]:
            """Maps virus_x0020__hemisphere to aind model."""
            return (
                None
                if self._nsb.virus_x0020__hemisphere is None
                else {
                    self._nsb.virus_x0020__hemisphere.SELECT: None,
                    self._nsb.virus_x0020__hemisphere.LEFT: None,
                    self._nsb.virus_x0020__hemisphere.RIGHT: None,
                }.get(self._nsb.virus_x0020__hemisphere, None)
            )
    
        @property
        def aind_virus_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps virus_x0020_a_x002f_p to aind model."""
            return self._nsb.virus_x0020_a_x002f_p

    @property
        def aind_fiber_x0020__implant5_x00_001(self) -> Optional[str]:
            """Maps fiber_x0020__implant5_x00_001 to aind model."""
            return self._nsb.fiber_x0020__implant5_x00_001

    @property
        def aind_burr_x0020_6_x0020__injec_006(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020__injec_006 to aind model."""
            return self._nsb.burr_x0020_6_x0020__injec_006

    @property
        def aind_burr_x0020_3_x0020__injec_007(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__injec_007 to aind model."""
            return self._nsb.burr_x0020_3_x0020__injec_007

    @property
        def aind_burr_x0020_6_x0020_d_x002_001(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020_d_x002_001 to aind model."""
            return self._nsb.burr_x0020_6_x0020_d_x002_001

    @property
        def aind_burr_x0020_hole_x0020_3(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_3 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_3 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_3.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_3.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_3.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_3.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_3, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_4(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_4 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_4 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_4.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_4.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_4.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_4.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_4, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_5(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_5 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_5 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_5.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_5.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_5.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_5.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_5, None)
            )
    
        @property
        def aind_burr_x0020_hole_x0020_6(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_6 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_6 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_6.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_6.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_6.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_6.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_6, None)
            )
    
        @property
        def aind_care_x0020__moduele(self) -> Optional[Any]:
            """Maps care_x0020__moduele to aind model."""
            return (
                None
                if self._nsb.care_x0020__moduele is None
                else {
                    self._nsb.care_x0020__moduele.SELECT: None,
                    self._nsb.care_x0020__moduele.CM_S_01_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_01_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_03_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_03_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_04_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_04_C_D: None,
                }.get(self._nsb.care_x0020__moduele, None)
            )
    
        @property
        def aind_color_tag(self) -> Optional[str]:
            """Maps color_tag to aind model."""
            return self._nsb.color_tag

    @property
        def aind_link_title(self) -> Optional[str]:
            """Maps link_title to aind model."""
            return self._nsb.link_title

    @property
        def aind_burr_x0020_2_x0020_d_x002(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020_d_x002 to aind model."""
            return self._nsb.burr_x0020_2_x0020_d_x002

    @property
        def aind_burr_x0020_4_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__injec to aind model."""
            return self._nsb.burr_x0020_4_x0020__injec

    @property
        def aind_burr_x0020_3_x0020__injec_006(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__injec_006 to aind model."""
            return self._nsb.burr_x0020_3_x0020__injec_006

    @property
        def aind_burr_x0020_6_x0020__injec_005(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020__injec_005 to aind model."""
            return self._nsb.burr_x0020_6_x0020__injec_005

    @property
        def aind_link_title_no_menu(self) -> Optional[str]:
            """Maps link_title_no_menu to aind model."""
            return self._nsb.link_title_no_menu

    @property
        def aind_burr2_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr2_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__virus_x0020 is None
                else {
                    self._nsb.burr2_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr2_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr3_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__injection_x0 is None
                else {
                    self._nsb.burr3_x0020__injection_x0.SELECT: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr3_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr3_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr3_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__perform_x002 is None
                else {
                    self._nsb.burr3_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr3_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr3_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr3_x0020__status(self) -> Optional[Any]:
            """Maps burr3_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__status is None
                else {
                    self._nsb.burr3_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr3_x0020__status, None)
            )
    
        @property
        def aind_burr3_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr3_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__virus_x0020 is None
                else {
                    self._nsb.burr3_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr3_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr3_x0020_a_x002f_p to aind model."""
            return self._nsb.burr3_x0020_a_x002f_p

    @property
        def aind_burr_x0020_5_x0020_intend_001(self) -> Optional[Any]:
            """Maps burr_x0020_5_x0020_intend_001 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_5_x0020_intend_001 is None
                else {
                    self._nsb.burr_x0020_5_x0020_intend_001.N_A: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.DOPAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.SEROTONIN: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.HISTAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.GLUTAMATE: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.GABA: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.CALCIUM: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.VOLTAGE: None,
                    self._nsb.burr_x0020_5_x0020_intend_001.CONTROL: None,
                }.get(self._nsb.burr_x0020_5_x0020_intend_001, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_5_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_5_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_5_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_5_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_5_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_5_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_5_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_5_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020_m_x002(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020_m_x002 to aind model."""
            return self._nsb.burr_x0020_5_x0020_m_x002

    @property
        def aind_burr_x0020_2_x0020__spina(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020__spina to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020__spina is None
                else {
                    self._nsb.burr_x0020_2_x0020__spina.SELECT: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_C1_C2: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_C2_C3: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_C3_C4: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_C4_C5: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_C6_C7: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_C7_C8: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_C8_T1: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_T1_T2: None,
                }.get(self._nsb.burr_x0020_2_x0020__spina, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020_d_x002(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020_d_x002 to aind model."""
            return self._nsb.burr_x0020_2_x0020_d_x002

    @property
        def aind_burr_x0020_4_x0020__injec_001(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__injec_001 to aind model."""
            return self._nsb.burr_x0020_4_x0020__injec_001

    @property
        def aind_app_author(self) -> Optional[str]:
            """Maps app_author to aind model."""
            return self._nsb.app_author

    @property
        def aind_burr_x0020_hole_x0020_6(self) -> Optional[Any]:
            """Maps burr_x0020_hole_x0020_6 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_hole_x0020_6 is None
                else {
                    self._nsb.burr_x0020_hole_x0020_6.SELECT: None,
                    self._nsb.burr_x0020_hole_x0020_6.STEREOTAXIC__INJECTION: None,
                    self._nsb.burr_x0020_hole_x0020_6.FIBER__IMPLANT: None,
                    self._nsb.burr_x0020_hole_x0020_6.STEREOTAXIC__INJECTION__F: None,
                }.get(self._nsb.burr_x0020_hole_x0020_6, None)
            )
    
        @property
        def aind_care_x0020__moduele(self) -> Optional[Any]:
            """Maps care_x0020__moduele to aind model."""
            return (
                None
                if self._nsb.care_x0020__moduele is None
                else {
                    self._nsb.care_x0020__moduele.SELECT: None,
                    self._nsb.care_x0020__moduele.CM_S_01_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_01_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_03_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_03_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_04_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_04_C_D: None,
                }.get(self._nsb.care_x0020__moduele, None)
            )
    
        @property
        def aind_color_tag(self) -> Optional[str]:
            """Maps color_tag to aind model."""
            return self._nsb.color_tag

    @property
        def aind_burr_x0020_6_x0020_intend_001(self) -> Optional[Any]:
            """Maps burr_x0020_6_x0020_intend_001 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_6_x0020_intend_001 is None
                else {
                    self._nsb.burr_x0020_6_x0020_intend_001.N_A: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.DOPAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.SEROTONIN: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.HISTAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.GLUTAMATE: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.GABA: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.CALCIUM: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.VOLTAGE: None,
                    self._nsb.burr_x0020_6_x0020_intend_001.CONTROL: None,
                }.get(self._nsb.burr_x0020_6_x0020_intend_001, None)
            )
    
        @property
        def aind_burr_x0020_6_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_6_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_6_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_6_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_6_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_6_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_6_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_6_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_6_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_6_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_6_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_6_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_6_x0020_m_x002(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020_m_x002 to aind model."""
            return self._nsb.burr_x0020_6_x0020_m_x002

    @property
        def aind_burr3_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr3_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__perform_x002 is None
                else {
                    self._nsb.burr3_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr3_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr3_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr3_x0020__status(self) -> Optional[Any]:
            """Maps burr3_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__status is None
                else {
                    self._nsb.burr3_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr3_x0020__status, None)
            )
    
        @property
        def aind_burr3_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr3_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__virus_x0020 is None
                else {
                    self._nsb.burr3_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr3_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr3_x0020_a_x002f_p to aind model."""
            return self._nsb.burr3_x0020_a_x002f_p

    @property
        def aind_burr_x0020_1_x0020__injec_007(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__injec_007 to aind model."""
            return self._nsb.burr_x0020_1_x0020__injec_007

    @property
        def aind_burr_x0020_5_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_5_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_5_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_5_x0020__fiber.STANDARD_PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_5_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_5_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020__hemis(self) -> Optional[Any]:
            """Maps burr_x0020_5_x0020__hemis to aind model."""
            return (
                None
                if self._nsb.burr_x0020_5_x0020__hemis is None
                else {
                    self._nsb.burr_x0020_5_x0020__hemis.SELECT: None,
                    self._nsb.burr_x0020_5_x0020__hemis.LEFT: None,
                    self._nsb.burr_x0020_5_x0020__hemis.RIGHT: None,
                }.get(self._nsb.burr_x0020_5_x0020__hemis, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__injec to aind model."""
            return self._nsb.burr_x0020_5_x0020__injec

    @property
        def aind_burr_x0020_6_x0020_d_x002(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020_d_x002 to aind model."""
            return self._nsb.burr_x0020_6_x0020_d_x002

    @property
        def aind_burr_x0020_1_x0020__inten(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020__inten to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020__inten is None
                else {
                    self._nsb.burr_x0020_1_x0020__inten.FRP__FRONTAL_POLE_CEREBRA: None,
                    self._nsb.burr_x0020_1_x0020__inten.M_OP__PRIMARY_MOTOR_AREA: None,
                    self._nsb.burr_x0020_1_x0020__inten.M_OS__SECONDARY_MOTOR_ARE: None,
                    self._nsb.burr_x0020_1_x0020__inten.S_SP_N__PRIMARY_SOMATOSEN: None,
                    self._nsb.burr_x0020_1_x0020__inten.S_SP_BFD__PRIMARY_SOMATOS: None,
                    self._nsb.burr_x0020_1_x0020__inten.S_SP_LL__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_1_x0020__inten.S_SP_M__PRIMARY_SOMATOSEN: None,
                    self._nsb.burr_x0020_1_x0020__inten.S_SP_UL__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_1_x0020__inten.S_SP_TR__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_1_x0020__inten.S_SP_UN__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_1_x0020__inten.S_SS__SUPPLEMENTAL_SOMATO: None,
                    self._nsb.burr_x0020_1_x0020__inten.GU__GUSTATORY_AREAS: None,
                    self._nsb.burr_x0020_1_x0020__inten.VISC__VISCERAL_AREA: None,
                    self._nsb.burr_x0020_1_x0020__inten.AU_DD__DORSAL_AUDITORY_AR: None,
                    self._nsb.burr_x0020_1_x0020__inten.AU_DP__PRIMARY_AUDITORY_A: None,
                    self._nsb.burr_x0020_1_x0020__inten.AU_DPO__POSTERIOR_AUDITOR: None,
                    self._nsb.burr_x0020_1_x0020__inten.AU_DV__VENTRAL_AUDITORY_A: None,
                    self._nsb.burr_x0020_1_x0020__inten.VI_SAL__ANTEROLATERAL_VIS: None,
                    self._nsb.burr_x0020_1_x0020__inten.VI_SAM__ANTEROMEDIAL_VISU: None,
                    self._nsb.burr_x0020_1_x0020__inten.VI_SL__LATERAL_VISUAL_ARE: None,
                    self._nsb.burr_x0020_1_x0020__inten.VI_SP__PRIMARY_VISUAL_ARE: None,
                    self._nsb.burr_x0020_1_x0020__inten.VI_SPL__POSTEROLATERAL_VI: None,
                    self._nsb.burr_x0020_1_x0020__inten.VI_SPM_POSTEROMEDIAL_VISU: None,
                    self._nsb.burr_x0020_1_x0020__inten.VI_SLI__LATEROINTERMEDIAT: None,
                    self._nsb.burr_x0020_1_x0020__inten.VI_SPOR__POSTRHINAL_AREA: None,
                    self._nsb.burr_x0020_1_x0020__inten.AC_AD__ANTERIOR_CINGULATE: None,
                    self._nsb.burr_x0020_1_x0020__inten.AC_AV__ANTERIOR_CINGULATE: None,
                    self._nsb.burr_x0020_1_x0020__inten.PL__PRELIMBIC_AREA: None,
                    self._nsb.burr_x0020_1_x0020__inten.ILA__INFRALIMBIC_AREA: None,
                    self._nsb.burr_x0020_1_x0020__inten.OR_BL__ORBITAL_AREA_LATER: None,
                    self._nsb.burr_x0020_1_x0020__inten.OR_BM__ORBITAL_AREA_MEDIA: None,
                    self._nsb.burr_x0020_1_x0020__inten.OR_BV__ORBITAL_AREA_VENTR: None,
                    self._nsb.burr_x0020_1_x0020__inten.OR_BVL__ORBITAL_AREA_VENT: None,
                    self._nsb.burr_x0020_1_x0020__inten.A_ID__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_1_x0020__inten.A_IP__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_1_x0020__inten.A_IV__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_1_x0020__inten.RS_PAGL__RETROSPLENIAL_AR: None,
                    self._nsb.burr_x0020_1_x0020__inten.RS_PD__RETROSPLENIAL_AREA: None,
                    self._nsb.burr_x0020_1_x0020__inten.RS_PV__RETROSPLENIAL_AREA: None,
                    self._nsb.burr_x0020_1_x0020__inten.VI_SA__ANTERIOR_AREA: None,
                    self._nsb.burr_x0020_1_x0020__inten.VI_SRL__ROSTROLATERAL_VIS: None,
                    self._nsb.burr_x0020_1_x0020__inten.T_EA__TEMPORAL_ASSOCIATIO: None,
                    self._nsb.burr_x0020_1_x0020__inten.PERI__PERIRHINAL_AREA: None,
                    self._nsb.burr_x0020_1_x0020__inten.ECT__ECTORHINAL_AREA: None,
                    self._nsb.burr_x0020_1_x0020__inten.MOB__MAIN_OLFACTORY_BULB: None,
                    self._nsb.burr_x0020_1_x0020__inten.AOB__ACCESSORY_OLFACTORY: None,
                    self._nsb.burr_x0020_1_x0020__inten.AON__ANTERIOR_OLFACTORY_N: None,
                    self._nsb.burr_x0020_1_x0020__inten.T_TD__TAENIA_TECTA_DORSAL: None,
                    self._nsb.burr_x0020_1_x0020__inten.T_TV__TAENIA_TECTA_VENTRA: None,
                    self._nsb.burr_x0020_1_x0020__inten.DP__DORSAL_PEDUNCULAR_ARE: None,
                    self._nsb.burr_x0020_1_x0020__inten.PIR__PIRIFORM_AREA: None,
                    self._nsb.burr_x0020_1_x0020__inten.NLOT__NUCLEUS_OF_THE_LATE: None,
                    self._nsb.burr_x0020_1_x0020__inten.CO_AA__CORTICAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_1_x0020__inten.CO_AP__CORTICAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_1_x0020__inten.PAA__PIRIFORM_AMYGDALAR_A: None,
                    self._nsb.burr_x0020_1_x0020__inten.TR__POSTPIRIFORM_TRANSITI: None,
                    self._nsb.burr_x0020_1_x0020__inten.CA1__FIELD_CA1: None,
                    self._nsb.burr_x0020_1_x0020__inten.CA2__FIELD_CA2: None,
                    self._nsb.burr_x0020_1_x0020__inten.CA3__FIELD_CA3: None,
                    self._nsb.burr_x0020_1_x0020__inten.DG__DENTATE_GYRUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.FC__FASCIOLA_CINEREA: None,
                    self._nsb.burr_x0020_1_x0020__inten.IG__INDUSEUM_GRISEUM: None,
                    self._nsb.burr_x0020_1_x0020__inten.EN_TL__ENTORHINAL_AREA_LA: None,
                    self._nsb.burr_x0020_1_x0020__inten.EN_TM__ENTORHINAL_AREA_ME: None,
                    self._nsb.burr_x0020_1_x0020__inten.PAR__PARASUBICULUM: None,
                    self._nsb.burr_x0020_1_x0020__inten.POST__POSTSUBICULUM: None,
                    self._nsb.burr_x0020_1_x0020__inten.PRE__PRESUBICULUM: None,
                    self._nsb.burr_x0020_1_x0020__inten.SUB__SUBICULUM: None,
                    self._nsb.burr_x0020_1_x0020__inten.PRO_S__PROSUBICULUM: None,
                    self._nsb.burr_x0020_1_x0020__inten.HATA__HIPPOCAMPO_AMYGDALA: None,
                    self._nsb.burr_x0020_1_x0020__inten.A_PR__AREA_PROSTRIATA: None,
                    self._nsb.burr_x0020_1_x0020__inten.CLA__CLAUSTRUM: None,
                    self._nsb.burr_x0020_1_x0020__inten.E_PD__ENDOPIRIFORM_NUCLEU: None,
                    self._nsb.burr_x0020_1_x0020__inten.E_PV__ENDOPIRIFORM_NUCLEU: None,
                    self._nsb.burr_x0020_1_x0020__inten.LA__LATERAL_AMYGDALAR_NUC: None,
                    self._nsb.burr_x0020_1_x0020__inten.BLA__BASOLATERAL_AMYGDALA: None,
                    self._nsb.burr_x0020_1_x0020__inten.BMA__BASOMEDIAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_1_x0020__inten.PA__POSTERIOR_AMYGDALAR_N: None,
                    self._nsb.burr_x0020_1_x0020__inten.CP__CAUDOPUTAMEN: None,
                    self._nsb.burr_x0020_1_x0020__inten.ACB__NUCLEUS_ACCUMBENS: None,
                    self._nsb.burr_x0020_1_x0020__inten.FS__FUNDUS_OF_STRIATUM: None,
                    self._nsb.burr_x0020_1_x0020__inten.OT__OLFACTORY_TUBERCLE: None,
                    self._nsb.burr_x0020_1_x0020__inten.L_SC__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.L_SR__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.L_SV__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.SF__SEPTOFIMBRIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.SH__SEPTOHIPPOCAMPAL_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.AAA__ANTERIOR_AMYGDALAR_A: None,
                    self._nsb.burr_x0020_1_x0020__inten.BA__BED_NUCLEUS_OF_THE_AC: None,
                    self._nsb.burr_x0020_1_x0020__inten.CEA__CENTRAL_AMYGDALAR_NU: None,
                    self._nsb.burr_x0020_1_x0020__inten.IA__INTERCALATED_AMYGDALA: None,
                    self._nsb.burr_x0020_1_x0020__inten.MEA__MEDIAL_AMYGDALAR_NUC: None,
                    self._nsb.burr_x0020_1_x0020__inten.G_PE__GLOBUS_PALLIDUS_EXT: None,
                    self._nsb.burr_x0020_1_x0020__inten.G_PI__GLOBUS_PALLIDUS_INT: None,
                    self._nsb.burr_x0020_1_x0020__inten.SI__SUBSTANTIA_INNOMINATA: None,
                    self._nsb.burr_x0020_1_x0020__inten.MA__MAGNOCELLULAR_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.MS__MEDIAL_SEPTAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.NDB__DIAGONAL_BAND_NUCLEU: None,
                    self._nsb.burr_x0020_1_x0020__inten.TRS__TRIANGULAR_NUCLEUS_O: None,
                    self._nsb.burr_x0020_1_x0020__inten.BST__BED_NUCLEI_OF_THE_ST: None,
                    self._nsb.burr_x0020_1_x0020__inten.VAL__VENTRAL_ANTERIOR_LAT: None,
                    self._nsb.burr_x0020_1_x0020__inten.VM__VENTRAL_MEDIAL_NUCLEU: None,
                    self._nsb.burr_x0020_1_x0020__inten.VPL__VENTRAL_POSTEROLATER: None,
                    self._nsb.burr_x0020_1_x0020__inten.VP_LPC__VENTRAL_POSTEROLA: None,
                    self._nsb.burr_x0020_1_x0020__inten.VPM__VENTRAL_POSTEROMEDIA: None,
                    self._nsb.burr_x0020_1_x0020__inten.VP_MPC__VENTRAL_POSTEROME: None,
                    self._nsb.burr_x0020_1_x0020__inten.PO_T__POSTERIOR_TRIANGULA: None,
                    self._nsb.burr_x0020_1_x0020__inten.SPF__SUBPARAFASCICULAR_NU: None,
                    self._nsb.burr_x0020_1_x0020__inten.SPA__SUBPARAFASCICULAR_AR: None,
                    self._nsb.burr_x0020_1_x0020__inten.PP__PERIPEDUNCULAR_NUCLEU: None,
                    self._nsb.burr_x0020_1_x0020__inten.MG__MEDIAL_GENICULATE_COM: None,
                    self._nsb.burr_x0020_1_x0020__inten.L_GD__DORSAL_PART_OF_THE: None,
                    self._nsb.burr_x0020_1_x0020__inten.LP__LATERAL_POSTERIOR_NUC: None,
                    self._nsb.burr_x0020_1_x0020__inten.PO__POSTERIOR_COMPLEX_OF: None,
                    self._nsb.burr_x0020_1_x0020__inten.POL__POSTERIOR_LIMITING_N: None,
                    self._nsb.burr_x0020_1_x0020__inten.SGN__SUPRAGENICULATE_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.ETH__ETHMOID_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_1_x0020__inten.AV__ANTEROVENTRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.AM__ANTEROMEDIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.AD__ANTERODORSAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.IAM__INTERANTEROMEDIAL_NU: None,
                    self._nsb.burr_x0020_1_x0020__inten.IAD__INTERANTERODORSAL_NU: None,
                    self._nsb.burr_x0020_1_x0020__inten.LD__LATERAL_DORSAL_NUCLEU: None,
                    self._nsb.burr_x0020_1_x0020__inten.IMD__INTERMEDIODORSAL_NUC: None,
                    self._nsb.burr_x0020_1_x0020__inten.MD__MEDIODORSAL_NUCLEUS_O: None,
                    self._nsb.burr_x0020_1_x0020__inten.SMT__SUBMEDIAL_NUCLEUS_OF: None,
                    self._nsb.burr_x0020_1_x0020__inten.PR__PERIREUNENSIS_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.PVT__PARAVENTRICULAR_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.PT__PARATAENIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.RE__NUCLEUS_OF_REUNIENS: None,
                    self._nsb.burr_x0020_1_x0020__inten.XI__XIPHOID_THALAMIC_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.RH__RHOMBOID_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.CM__CENTRAL_MEDIAL_NUCLEU: None,
                    self._nsb.burr_x0020_1_x0020__inten.PCN__PARACENTRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.CL__CENTRAL_LATERAL_NUCLE: None,
                    self._nsb.burr_x0020_1_x0020__inten.PF__PARAFASCICULAR_NUCLEU: None,
                    self._nsb.burr_x0020_1_x0020__inten.PIL__POSTERIOR_INTRALAMIN: None,
                    self._nsb.burr_x0020_1_x0020__inten.RT__RETICULAR_NUCLEUS_OF: None,
                    self._nsb.burr_x0020_1_x0020__inten.IGL__INTERGENICULATE_LEAF: None,
                    self._nsb.burr_x0020_1_x0020__inten.INT_G__INTERMEDIATE_GENIC: None,
                    self._nsb.burr_x0020_1_x0020__inten.L_GV__VENTRAL_PART_OF_THE: None,
                    self._nsb.burr_x0020_1_x0020__inten.SUB_G__SUBGENICULATE_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.MH__MEDIAL_HABENULA: None,
                    self._nsb.burr_x0020_1_x0020__inten.LH__LATERAL_HABENULA: None,
                    self._nsb.burr_x0020_1_x0020__inten.SO__SUPRAOPTIC_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.PVH__PARAVENTRICULAR_HYPO: None,
                    self._nsb.burr_x0020_1_x0020__inten.P_VA__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_1_x0020__inten.P_VI__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_1_x0020__inten.ARH__ARCUATE_HYPOTHALAMIC: None,
                    self._nsb.burr_x0020_1_x0020__inten.ADP__ANTERODORSAL_PREOPTI: None,
                    self._nsb.burr_x0020_1_x0020__inten.AVP__ANTEROVENTRAL_PREOPT: None,
                    self._nsb.burr_x0020_1_x0020__inten.AVPV__ANTEROVENTRAL_PERIV: None,
                    self._nsb.burr_x0020_1_x0020__inten.DMH__DORSOMEDIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.MEPO__MEDIAN_PREOPTIC_NUC: None,
                    self._nsb.burr_x0020_1_x0020__inten.MPO__MEDIAL_PREOPTIC_AREA: None,
                    self._nsb.burr_x0020_1_x0020__inten.PS__PARASTRIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.P_VP__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_1_x0020__inten.P_VPO__PERIVENTRICULAR_HY: None,
                    self._nsb.burr_x0020_1_x0020__inten.SBPV__SUBPARAVENTRICULAR: None,
                    self._nsb.burr_x0020_1_x0020__inten.SCH__SUPRACHIASMATIC_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.SFO__SUBFORNICAL_ORGAN: None,
                    self._nsb.burr_x0020_1_x0020__inten.VMPO__VENTROMEDIAL_PREOPT: None,
                    self._nsb.burr_x0020_1_x0020__inten.VLPO__VENTROLATERAL_PREOP: None,
                    self._nsb.burr_x0020_1_x0020__inten.AHN__ANTERIOR_HYPOTHALAMI: None,
                    self._nsb.burr_x0020_1_x0020__inten.LM__LATERAL_MAMMILLARY_NU: None,
                    self._nsb.burr_x0020_1_x0020__inten.MM__MEDIAL_MAMMILLARY_NUC: None,
                    self._nsb.burr_x0020_1_x0020__inten.SUM__SUPRAMAMMILLARY_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.TM__TUBEROMAMMILLARY_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.MPN__MEDIAL_PREOPTIC_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.P_MD__DORSAL_PREMAMMILLAR: None,
                    self._nsb.burr_x0020_1_x0020__inten.P_MV__VENTRAL_PREMAMMILLA: None,
                    self._nsb.burr_x0020_1_x0020__inten.PV_HD__PARAVENTRICULAR_HY: None,
                    self._nsb.burr_x0020_1_x0020__inten.VMH__VENTROMEDIAL_HYPOTHA: None,
                    self._nsb.burr_x0020_1_x0020__inten.PH__POSTERIOR_HYPOTHALAMI: None,
                    self._nsb.burr_x0020_1_x0020__inten.LHA__LATERAL_HYPOTHALAMIC: None,
                    self._nsb.burr_x0020_1_x0020__inten.LPO__LATERAL_PREOPTIC_ARE: None,
                    self._nsb.burr_x0020_1_x0020__inten.PSTN__PARASUBTHALAMIC_NUC: None,
                    self._nsb.burr_x0020_1_x0020__inten.PE_F__PERIFORNICAL_NUCLEU: None,
                    self._nsb.burr_x0020_1_x0020__inten.RCH__RETROCHIASMATIC_AREA: None,
                    self._nsb.burr_x0020_1_x0020__inten.STN__SUBTHALAMIC_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.TU__TUBERAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.ZI__ZONA_INCERTA: None,
                    self._nsb.burr_x0020_1_x0020__inten.S_CS__SUPERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.IC__INFERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.NB__NUCLEUS_OF_THE_BRACHI: None,
                    self._nsb.burr_x0020_1_x0020__inten.SAG__NUCLEUS_SAGULUM: None,
                    self._nsb.burr_x0020_1_x0020__inten.PBG__PARABIGEMINAL_NUCLEU: None,
                    self._nsb.burr_x0020_1_x0020__inten.S_NR__SUBSTANTIA_NIGRA_RE: None,
                    self._nsb.burr_x0020_1_x0020__inten.VTA__VENTRAL_TEGMENTAL_AR: None,
                    self._nsb.burr_x0020_1_x0020__inten.PN__PARANIGRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.RR__MIDBRAIN_RETICULAR_NU: None,
                    self._nsb.burr_x0020_1_x0020__inten.MRN__MIDBRAIN_RETICULAR_N: None,
                    self._nsb.burr_x0020_1_x0020__inten.S_CM__SUPERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.PAG__PERIAQUEDUCTAL_GRAY: None,
                    self._nsb.burr_x0020_1_x0020__inten.APN__ANTERIOR_PRETECTAL_N: None,
                    self._nsb.burr_x0020_1_x0020__inten.MPT__MEDIAL_PRETECTAL_ARE: None,
                    self._nsb.burr_x0020_1_x0020__inten.NOT__NUCLEUS_OF_THE_OPTIC: None,
                    self._nsb.burr_x0020_1_x0020__inten.NPC__NUCLEUS_OF_THE_POSTE: None,
                    self._nsb.burr_x0020_1_x0020__inten.OP__OLIVARY_PRETECTAL_NUC: None,
                    self._nsb.burr_x0020_1_x0020__inten.PPT__POSTERIOR_PRETECTAL: None,
                    self._nsb.burr_x0020_1_x0020__inten.RPF__RETROPARAFASCICULAR: None,
                    self._nsb.burr_x0020_1_x0020__inten.CUN__CUNEIFORM_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.RN__RED_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.III__OCULOMOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.MA3__MEDIAL_ACCESORY_OCUL: None,
                    self._nsb.burr_x0020_1_x0020__inten.EW__EDINGER__WESTPHAL_NUC: None,
                    self._nsb.burr_x0020_1_x0020__inten.IV__TROCHLEAR_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.PA4__PARATROCHLEAR_NUCLEU: None,
                    self._nsb.burr_x0020_1_x0020__inten.VTN__VENTRAL_TEGMENTAL_NU: None,
                    self._nsb.burr_x0020_1_x0020__inten.AT__ANTERIOR_TEGMENTAL_NU: None,
                    self._nsb.burr_x0020_1_x0020__inten.LT__LATERAL_TERMINAL_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.DT__DORSAL_TERMINAL_NUCLE: None,
                    self._nsb.burr_x0020_1_x0020__inten.MT__MEDIAL_TERMINAL_NUCLE: None,
                    self._nsb.burr_x0020_1_x0020__inten.S_NC__SUBSTANTIA_NIGRA_CO: None,
                    self._nsb.burr_x0020_1_x0020__inten.PPN__PEDUNCULOPONTINE_NUC: None,
                    self._nsb.burr_x0020_1_x0020__inten.IF__INTERFASCICULAR_NUCLE: None,
                    self._nsb.burr_x0020_1_x0020__inten.IPN__INTERPEDUNCULAR_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.RL__ROSTRAL_LINEAR_NUCLEU: None,
                    self._nsb.burr_x0020_1_x0020__inten.CLI__CENTRAL_LINEAR_NUCLE: None,
                    self._nsb.burr_x0020_1_x0020__inten.DR__DORSAL_NUCLEUS_RAPHE: None,
                    self._nsb.burr_x0020_1_x0020__inten.NLL__NUCLEUS_OF_THE_LATER: None,
                    self._nsb.burr_x0020_1_x0020__inten.PSV__PRINCIPAL_SENSORY_NU: None,
                    self._nsb.burr_x0020_1_x0020__inten.PB__PARABRACHIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.SOC__SUPERIOR_OLIVARY_COM: None,
                    self._nsb.burr_x0020_1_x0020__inten.B__BARRINGTON_S_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.DTN__DORSAL_TEGMENTAL_NUC: None,
                    self._nsb.burr_x0020_1_x0020__inten.PD_TG__POSTERODORSAL_TEGM: None,
                    self._nsb.burr_x0020_1_x0020__inten.PCG__PONTINE_CENTRAL_GRAY: None,
                    self._nsb.burr_x0020_1_x0020__inten.PG__PONTINE_GRAY: None,
                    self._nsb.burr_x0020_1_x0020__inten.PR_NC__PONTINE_RETICULAR: None,
                    self._nsb.burr_x0020_1_x0020__inten.SG__SUPRAGENUAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.SUT__SUPRATRIGEMINAL_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.TRN__TEGMENTAL_RETICULAR: None,
                    self._nsb.burr_x0020_1_x0020__inten.V__MOTOR_NUCLEUS_OF_TRIGE: None,
                    self._nsb.burr_x0020_1_x0020__inten.P5__PERITRIGEMINAL_ZONE: None,
                    self._nsb.burr_x0020_1_x0020__inten.ACS5__ACCESSORY_TRIGEMINA: None,
                    self._nsb.burr_x0020_1_x0020__inten.PC5__PARVICELLULAR_MOTOR: None,
                    self._nsb.burr_x0020_1_x0020__inten.I5__INTERTRIGEMINAL_NUCLE: None,
                    self._nsb.burr_x0020_1_x0020__inten.CS__SUPERIOR_CENTRAL_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.LC__LOCUS_CERULEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.LDT__LATERODORSAL_TEGMENT: None,
                    self._nsb.burr_x0020_1_x0020__inten.NI__NUCLEUS_INCERTUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.PR_NR__PONTINE_RETICULAR: None,
                    self._nsb.burr_x0020_1_x0020__inten.RPO__NUCLEUS_RAPHE_PONTIS: None,
                    self._nsb.burr_x0020_1_x0020__inten.SLC__SUBCERULEUS_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.SLD__SUBLATERODORSAL_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.MY__MEDULLA: None,
                    self._nsb.burr_x0020_1_x0020__inten.AP__AREA_POSTREMA: None,
                    self._nsb.burr_x0020_1_x0020__inten.DCO__DORSAL_COCHLEAR_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.VCO__VENTRAL_COCHLEAR_NUC: None,
                    self._nsb.burr_x0020_1_x0020__inten.CU__CUNEATE_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.GR__GRACILE_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.ECU__EXTERNAL_CUNEATE_NUC: None,
                    self._nsb.burr_x0020_1_x0020__inten.NTB__NUCLEUS_OF_THE_TRAPE: None,
                    self._nsb.burr_x0020_1_x0020__inten.NTS__NUCLEUS_OF_THE_SOLIT: None,
                    self._nsb.burr_x0020_1_x0020__inten.SPVC__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_1_x0020__inten.SPVI__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_1_x0020__inten.SPVO__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_1_x0020__inten.PA5__PARATRIGEMINAL_NUCLE: None,
                    self._nsb.burr_x0020_1_x0020__inten.VI__ABDUCENS_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.VII__FACIAL_MOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.AMB__NUCLEUS_AMBIGUUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.DMX__DORSAL_MOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.GRN__GIGANTOCELLULAR_RETI: None,
                    self._nsb.burr_x0020_1_x0020__inten.ICB__INFRACEREBELLAR_NUCL: None,
                    self._nsb.burr_x0020_1_x0020__inten.IO__INFERIOR_OLIVARY_COMP: None,
                    self._nsb.burr_x0020_1_x0020__inten.IRN__INTERMEDIATE_RETICUL: None,
                    self._nsb.burr_x0020_1_x0020__inten.ISN__INFERIOR_SALIVATORY: None,
                    self._nsb.burr_x0020_1_x0020__inten.LIN__LINEAR_NUCLEUS_OF_TH: None,
                    self._nsb.burr_x0020_1_x0020__inten.LRN__LATERAL_RETICULAR_NU: None,
                    self._nsb.burr_x0020_1_x0020__inten.MARN__MAGNOCELLULAR_RETIC: None,
                    self._nsb.burr_x0020_1_x0020__inten.MDRN__MEDULLARY_RETICULAR: None,
                    self._nsb.burr_x0020_1_x0020__inten.PARN__PARVICELLULAR_RETIC: None,
                    self._nsb.burr_x0020_1_x0020__inten.PAS__PARASOLITARY_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.PGRN__PARAGIGANTOCELLULAR: None,
                    self._nsb.burr_x0020_1_x0020__inten.NR__NUCLEUS_OF__ROLLER: None,
                    self._nsb.burr_x0020_1_x0020__inten.PRP__NUCLEUS_PREPOSITUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.PMR__PARAMEDIAN_RETICULAR: None,
                    self._nsb.burr_x0020_1_x0020__inten.PPY__PARAPYRAMIDAL_NUCLEU: None,
                    self._nsb.burr_x0020_1_x0020__inten.LAV__LATERAL_VESTIBULAR_N: None,
                    self._nsb.burr_x0020_1_x0020__inten.MV__MEDIAL_VESTIBULAR_NUC: None,
                    self._nsb.burr_x0020_1_x0020__inten.SPIV__SPINAL_VESTIBULAR_N: None,
                    self._nsb.burr_x0020_1_x0020__inten.SUV__SUPERIOR_VESTIBULAR: None,
                    self._nsb.burr_x0020_1_x0020__inten.X__NUCLEUS_X: None,
                    self._nsb.burr_x0020_1_x0020__inten.XII__HYPOGLOSSAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.Y__NUCLEUS_Y: None,
                    self._nsb.burr_x0020_1_x0020__inten.RM__NUCLEUS_RAPHE_MAGNUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.RPA__NUCLEUS_RAPHE_PALLID: None,
                    self._nsb.burr_x0020_1_x0020__inten.RO__NUCLEUS_RAPHE_OBSCURU: None,
                    self._nsb.burr_x0020_1_x0020__inten.LING__LINGULA_I: None,
                    self._nsb.burr_x0020_1_x0020__inten.CENT2__LOBULE_II: None,
                    self._nsb.burr_x0020_1_x0020__inten.CENT3__LOBULE_III: None,
                    self._nsb.burr_x0020_1_x0020__inten.CUL4_5__LOBULES_IV_V: None,
                    self._nsb.burr_x0020_1_x0020__inten.DEC__DECLIVE_VI: None,
                    self._nsb.burr_x0020_1_x0020__inten.FOTU__FOLIUM_TUBER_VERMIS: None,
                    self._nsb.burr_x0020_1_x0020__inten.PYR__PYRAMUS_VIII: None,
                    self._nsb.burr_x0020_1_x0020__inten.UVU__UVULA_IX: None,
                    self._nsb.burr_x0020_1_x0020__inten.NOD__NODULUS_X: None,
                    self._nsb.burr_x0020_1_x0020__inten.SIM__SIMPLE_LOBULE: None,
                    self._nsb.burr_x0020_1_x0020__inten.A_NCR1__CRUS_1: None,
                    self._nsb.burr_x0020_1_x0020__inten.A_NCR2__CRUS_2: None,
                    self._nsb.burr_x0020_1_x0020__inten.PRM__PARAMEDIAN_LOBULE: None,
                    self._nsb.burr_x0020_1_x0020__inten.COPY__COPULA_PYRAMIDIS: None,
                    self._nsb.burr_x0020_1_x0020__inten.PFL__PARAFLOCCULUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.FL__FLOCCULUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.FN__FASTIGIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.IP__INTERPOSED_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.DN__DENTATE_NUCLEUS: None,
                    self._nsb.burr_x0020_1_x0020__inten.VE_CB__VESTIBULOCEREBELLA: None,
                }.get(self._nsb.burr_x0020_1_x0020__inten, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__spina(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020__spina to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020__spina is None
                else {
                    self._nsb.burr_x0020_1_x0020__spina.SELECT: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_C1_C2: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_C2_C3: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_C3_C4: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_C4_C5: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_C6_C7: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_C7_C8: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_C8_T1: None,
                    self._nsb.burr_x0020_1_x0020__spina.BETWEEN_T1_T2: None,
                }.get(self._nsb.burr_x0020_1_x0020__spina, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020_d_x002(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020_d_x002 to aind model."""
            return self._nsb.burr_x0020_1_x0020_d_x002

    @property
        def aind_burr_x0020_4_x0020__injec_006(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__injec_006 to aind model."""
            return self._nsb.burr_x0020_4_x0020__injec_006

    @property
        def aind_behavior_x0020__curriculu(self) -> Optional[Any]:
            """Maps behavior_x0020__curriculu to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__curriculu is None
                else {
                    self._nsb.behavior_x0020__curriculu.N_2_3: None,
                    self._nsb.behavior_x0020__curriculu.N_2_3_1RWD_DELAY159: None,
                    self._nsb.behavior_x0020__curriculu.N_A: None,
                }.get(self._nsb.behavior_x0020__curriculu, None)
            )
    
        @property
        def aind_behavior_x0020__destinati(self) -> Optional[Any]:
            """Maps behavior_x0020__destinati to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__destinati is None
                else {
                    self._nsb.behavior_x0020__destinati.EPHYS: None,
                    self._nsb.behavior_x0020__destinati.OPHYS: None,
                    self._nsb.behavior_x0020__destinati.HSFP: None,
                    self._nsb.behavior_x0020__destinati.PERFUSION: None,
                    self._nsb.behavior_x0020__destinati.N_A: None,
                }.get(self._nsb.behavior_x0020__destinati, None)
            )
    
        @property
        def aind_behavior_x0020__fiber_x00(self) -> Optional[Any]:
            """Maps behavior_x0020__fiber_x00 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__fiber_x00 is None
                else {
                    self._nsb.behavior_x0020__fiber_x00.YES: None,
                    self._nsb.behavior_x0020__fiber_x00.NO: None,
                }.get(self._nsb.behavior_x0020__fiber_x00, None)
            )
    
        @property
        def aind_behavior_x0020__first_x00(self) -> Optional[Any]:
            """Maps behavior_x0020__first_x00 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__first_x00 is None
                else {
                    self._nsb.behavior_x0020__first_x00.N_1_1: None,
                    self._nsb.behavior_x0020__first_x00.N_1_2: None,
                    self._nsb.behavior_x0020__first_x00.N_2: None,
                    self._nsb.behavior_x0020__first_x00.N_3: None,
                    self._nsb.behavior_x0020__first_x00.N_4: None,
                    self._nsb.behavior_x0020__first_x00.N_5: None,
                    self._nsb.behavior_x0020__first_x00.N_6: None,
                    self._nsb.behavior_x0020__first_x00.FINAL: None,
                    self._nsb.behavior_x0020__first_x00.GRADUATED: None,
                    self._nsb.behavior_x0020__first_x00.N_A: None,
                }.get(self._nsb.behavior_x0020__first_x00, None)
            )
    
        @property
        def aind_behavior_x0020__first_x00_001(self) -> Optional[Any]:
            """Maps behavior_x0020__first_x00_001 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__first_x00_001 is None
                else {
                    self._nsb.behavior_x0020__first_x00_001.N_1_1: None,
                    self._nsb.behavior_x0020__first_x00_001.N_1_2: None,
                    self._nsb.behavior_x0020__first_x00_001.N_2: None,
                    self._nsb.behavior_x0020__first_x00_001.N_3: None,
                    self._nsb.behavior_x0020__first_x00_001.N_4: None,
                    self._nsb.behavior_x0020__first_x00_001.N_5: None,
                    self._nsb.behavior_x0020__first_x00_001.N_6: None,
                    self._nsb.behavior_x0020__first_x00_001.FINAL: None,
                    self._nsb.behavior_x0020__first_x00_001.GRADUATED: None,
                    self._nsb.behavior_x0020__first_x00_001.N_A: None,
                }.get(self._nsb.behavior_x0020__first_x00_001, None)
            )
    
        @property
        def aind_behavior_x0020__platform(self) -> Optional[Any]:
            """Maps behavior_x0020__platform to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__platform is None
                else {
                    self._nsb.behavior_x0020__platform.MINDSCOPE: None,
                    self._nsb.behavior_x0020__platform.FORAGING: None,
                    self._nsb.behavior_x0020__platform.VR: None,
                }.get(self._nsb.behavior_x0020__platform, None)
            )
    
        @property
        def aind_behavior_x0020__type(self) -> Optional[Any]:
            """Maps behavior_x0020__type to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__type is None
                else {
                    self._nsb.behavior_x0020__type.SELECT: None,
                    self._nsb.behavior_x0020__type.FORAGING: None,
                    self._nsb.behavior_x0020__type.FORAGING_FP: None,
                    self._nsb.behavior_x0020__type.WR__HAB: None,
                    self._nsb.behavior_x0020__type.HAB__ONLY: None,
                }.get(self._nsb.behavior_x0020__type, None)
            )
    
        @property
        def aind_behavior_x0020_fip_x0020(self) -> Optional[Any]:
            """Maps behavior_x0020_fip_x0020 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020_fip_x0020 is None
                else {
                    self._nsb.behavior_x0020_fip_x0020.N_A: None,
                    self._nsb.behavior_x0020_fip_x0020.NORMAL: None,
                    self._nsb.behavior_x0020_fip_x0020.AXON: None,
                }.get(self._nsb.behavior_x0020_fip_x0020, None)
            )
    
        @property
        def aind_black_x0020__cement(self) -> Optional[Any]:
            """Maps black_x0020__cement to aind model."""
            return (
                None
                if self._nsb.black_x0020__cement is None
                else {
                    self._nsb.black_x0020__cement.YES: None,
                    self._nsb.black_x0020__cement.NO: None,
                }.get(self._nsb.black_x0020__cement, None)
            )
    
        @property
        def aind_breg2_lamb(self) -> Optional[str]:
            """Maps breg2_lamb to aind model."""
            return self._nsb.breg2_lamb

    @property
        def aind_burr_x0020_5_x0020_d_x002(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020_d_x002 to aind model."""
            return self._nsb.burr_x0020_5_x0020_d_x002

    @property
        def aind_virus_x0020_m_x002f_l(self) -> Optional[str]:
            """Maps virus_x0020_m_x002f_l to aind model."""
            return self._nsb.virus_x0020_m_x002f_l

    @property
        def aind_burr_x0020_6_x0020__hemis(self) -> Optional[Any]:
            """Maps burr_x0020_6_x0020__hemis to aind model."""
            return (
                None
                if self._nsb.burr_x0020_6_x0020__hemis is None
                else {
                    self._nsb.burr_x0020_6_x0020__hemis.SELECT: None,
                    self._nsb.burr_x0020_6_x0020__hemis.LEFT: None,
                    self._nsb.burr_x0020_6_x0020__hemis.RIGHT: None,
                }.get(self._nsb.burr_x0020_6_x0020__hemis, None)
            )
    
        @property
        def aind_burr_x0020_6_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020__injec to aind model."""
            return self._nsb.burr_x0020_6_x0020__injec

    @property
        def aind_iso_x0020__on(self) -> Optional[str]:
            """Maps iso_x0020__on to aind model."""
            return self._nsb.iso_x0020__on

    @property
        def aind_weight_x0020_before_x0020(self) -> Optional[str]:
            """Maps weight_x0020_before_x0020 to aind model."""
            return self._nsb.weight_x0020_before_x0020

    @property
        def aind_burr_x0020_1_x0020_intend_001(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020_intend_001 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020_intend_001 is None
                else {
                    self._nsb.burr_x0020_1_x0020_intend_001.N_A: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.DOPAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.SEROTONIN: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.HISTAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.GLUTAMATE: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.GABA: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.CALCIUM: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.VOLTAGE: None,
                    self._nsb.burr_x0020_1_x0020_intend_001.CONTROL: None,
                }.get(self._nsb.burr_x0020_1_x0020_intend_001, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_1_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_1_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_1_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_1_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_1_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_1_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_2_x0020__fiber.STANDARD__PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_2_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_2_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020__injec to aind model."""
            return self._nsb.burr_x0020_2_x0020__injec

    @property
        def aind_burr_x0020_5_x0020__injec_005(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__injec_005 to aind model."""
            return self._nsb.burr_x0020_5_x0020__injec_005

    @property
        def aind_burr_x0020_3_x0020_d_x002(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020_d_x002 to aind model."""
            return self._nsb.burr_x0020_3_x0020_d_x002

    @property
        def aind_burr_x0020_3_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_3_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_3_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_3_x0020__fiber.STANDARD__PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_3_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_3_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_3_x0020__hemis(self) -> Optional[Any]:
            """Maps burr_x0020_3_x0020__hemis to aind model."""
            return (
                None
                if self._nsb.burr_x0020_3_x0020__hemis is None
                else {
                    self._nsb.burr_x0020_3_x0020__hemis.SELECT: None,
                    self._nsb.burr_x0020_3_x0020__hemis.LEFT: None,
                    self._nsb.burr_x0020_3_x0020__hemis.RIGHT: None,
                }.get(self._nsb.burr_x0020_3_x0020__hemis, None)
            )
    
        @property
        def aind_burr_x0020_3_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__injec to aind model."""
            return self._nsb.burr_x0020_3_x0020__injec

    @property
        def aind_burr_x0020_4_x0020__inten(self) -> Optional[Any]:
            """Maps burr_x0020_4_x0020__inten to aind model."""
            return (
                None
                if self._nsb.burr_x0020_4_x0020__inten is None
                else {
                    self._nsb.burr_x0020_4_x0020__inten.FRP__FRONTAL_POLE_CEREBRA: None,
                    self._nsb.burr_x0020_4_x0020__inten.M_OP__PRIMARY_MOTOR_AREA: None,
                    self._nsb.burr_x0020_4_x0020__inten.M_OS__SECONDARY_MOTOR_ARE: None,
                    self._nsb.burr_x0020_4_x0020__inten.S_SP_N__PRIMARY_SOMATOSEN: None,
                    self._nsb.burr_x0020_4_x0020__inten.S_SP_BFD__PRIMARY_SOMATOS: None,
                    self._nsb.burr_x0020_4_x0020__inten.S_SP_LL__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_4_x0020__inten.S_SP_M__PRIMARY_SOMATOSEN: None,
                    self._nsb.burr_x0020_4_x0020__inten.S_SP_UL__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_4_x0020__inten.S_SP_TR__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_4_x0020__inten.S_SP_UN__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_4_x0020__inten.S_SS__SUPPLEMENTAL_SOMATO: None,
                    self._nsb.burr_x0020_4_x0020__inten.GU__GUSTATORY_AREAS: None,
                    self._nsb.burr_x0020_4_x0020__inten.VISC__VISCERAL_AREA: None,
                    self._nsb.burr_x0020_4_x0020__inten.AU_DD__DORSAL_AUDITORY_AR: None,
                    self._nsb.burr_x0020_4_x0020__inten.AU_DP__PRIMARY_AUDITORY_A: None,
                    self._nsb.burr_x0020_4_x0020__inten.AU_DPO__POSTERIOR_AUDITOR: None,
                    self._nsb.burr_x0020_4_x0020__inten.AU_DV__VENTRAL_AUDITORY_A: None,
                    self._nsb.burr_x0020_4_x0020__inten.VI_SAL__ANTEROLATERAL_VIS: None,
                    self._nsb.burr_x0020_4_x0020__inten.VI_SAM__ANTEROMEDIAL_VISU: None,
                    self._nsb.burr_x0020_4_x0020__inten.VI_SL__LATERAL_VISUAL_ARE: None,
                    self._nsb.burr_x0020_4_x0020__inten.VI_SP__PRIMARY_VISUAL_ARE: None,
                    self._nsb.burr_x0020_4_x0020__inten.VI_SPL__POSTEROLATERAL_VI: None,
                    self._nsb.burr_x0020_4_x0020__inten.VI_SPM_POSTEROMEDIAL_VISU: None,
                    self._nsb.burr_x0020_4_x0020__inten.VI_SLI__LATEROINTERMEDIAT: None,
                    self._nsb.burr_x0020_4_x0020__inten.VI_SPOR__POSTRHINAL_AREA: None,
                    self._nsb.burr_x0020_4_x0020__inten.AC_AD__ANTERIOR_CINGULATE: None,
                    self._nsb.burr_x0020_4_x0020__inten.AC_AV__ANTERIOR_CINGULATE: None,
                    self._nsb.burr_x0020_4_x0020__inten.PL__PRELIMBIC_AREA: None,
                    self._nsb.burr_x0020_4_x0020__inten.ILA__INFRALIMBIC_AREA: None,
                    self._nsb.burr_x0020_4_x0020__inten.OR_BL__ORBITAL_AREA_LATER: None,
                    self._nsb.burr_x0020_4_x0020__inten.OR_BM__ORBITAL_AREA_MEDIA: None,
                    self._nsb.burr_x0020_4_x0020__inten.OR_BV__ORBITAL_AREA_VENTR: None,
                    self._nsb.burr_x0020_4_x0020__inten.OR_BVL__ORBITAL_AREA_VENT: None,
                    self._nsb.burr_x0020_4_x0020__inten.A_ID__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_4_x0020__inten.A_IP__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_4_x0020__inten.A_IV__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_4_x0020__inten.RS_PAGL__RETROSPLENIAL_AR: None,
                    self._nsb.burr_x0020_4_x0020__inten.RS_PD__RETROSPLENIAL_AREA: None,
                    self._nsb.burr_x0020_4_x0020__inten.RS_PV__RETROSPLENIAL_AREA: None,
                    self._nsb.burr_x0020_4_x0020__inten.VI_SA__ANTERIOR_AREA: None,
                    self._nsb.burr_x0020_4_x0020__inten.VI_SRL__ROSTROLATERAL_VIS: None,
                    self._nsb.burr_x0020_4_x0020__inten.T_EA__TEMPORAL_ASSOCIATIO: None,
                    self._nsb.burr_x0020_4_x0020__inten.PERI__PERIRHINAL_AREA: None,
                    self._nsb.burr_x0020_4_x0020__inten.ECT__ECTORHINAL_AREA: None,
                    self._nsb.burr_x0020_4_x0020__inten.MOB__MAIN_OLFACTORY_BULB: None,
                    self._nsb.burr_x0020_4_x0020__inten.AOB__ACCESSORY_OLFACTORY: None,
                    self._nsb.burr_x0020_4_x0020__inten.AON__ANTERIOR_OLFACTORY_N: None,
                    self._nsb.burr_x0020_4_x0020__inten.T_TD__TAENIA_TECTA_DORSAL: None,
                    self._nsb.burr_x0020_4_x0020__inten.T_TV__TAENIA_TECTA_VENTRA: None,
                    self._nsb.burr_x0020_4_x0020__inten.DP__DORSAL_PEDUNCULAR_ARE: None,
                    self._nsb.burr_x0020_4_x0020__inten.PIR__PIRIFORM_AREA: None,
                    self._nsb.burr_x0020_4_x0020__inten.NLOT__NUCLEUS_OF_THE_LATE: None,
                    self._nsb.burr_x0020_4_x0020__inten.CO_AA__CORTICAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_4_x0020__inten.CO_AP__CORTICAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_4_x0020__inten.PAA__PIRIFORM_AMYGDALAR_A: None,
                    self._nsb.burr_x0020_4_x0020__inten.TR__POSTPIRIFORM_TRANSITI: None,
                    self._nsb.burr_x0020_4_x0020__inten.CA1__FIELD_CA1: None,
                    self._nsb.burr_x0020_4_x0020__inten.CA2__FIELD_CA2: None,
                    self._nsb.burr_x0020_4_x0020__inten.CA3__FIELD_CA3: None,
                    self._nsb.burr_x0020_4_x0020__inten.DG__DENTATE_GYRUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.FC__FASCIOLA_CINEREA: None,
                    self._nsb.burr_x0020_4_x0020__inten.IG__INDUSEUM_GRISEUM: None,
                    self._nsb.burr_x0020_4_x0020__inten.EN_TL__ENTORHINAL_AREA_LA: None,
                    self._nsb.burr_x0020_4_x0020__inten.EN_TM__ENTORHINAL_AREA_ME: None,
                    self._nsb.burr_x0020_4_x0020__inten.PAR__PARASUBICULUM: None,
                    self._nsb.burr_x0020_4_x0020__inten.POST__POSTSUBICULUM: None,
                    self._nsb.burr_x0020_4_x0020__inten.PRE__PRESUBICULUM: None,
                    self._nsb.burr_x0020_4_x0020__inten.SUB__SUBICULUM: None,
                    self._nsb.burr_x0020_4_x0020__inten.PRO_S__PROSUBICULUM: None,
                    self._nsb.burr_x0020_4_x0020__inten.HATA__HIPPOCAMPO_AMYGDALA: None,
                    self._nsb.burr_x0020_4_x0020__inten.A_PR__AREA_PROSTRIATA: None,
                    self._nsb.burr_x0020_4_x0020__inten.CLA__CLAUSTRUM: None,
                    self._nsb.burr_x0020_4_x0020__inten.E_PD__ENDOPIRIFORM_NUCLEU: None,
                    self._nsb.burr_x0020_4_x0020__inten.E_PV__ENDOPIRIFORM_NUCLEU: None,
                    self._nsb.burr_x0020_4_x0020__inten.LA__LATERAL_AMYGDALAR_NUC: None,
                    self._nsb.burr_x0020_4_x0020__inten.BLA__BASOLATERAL_AMYGDALA: None,
                    self._nsb.burr_x0020_4_x0020__inten.BMA__BASOMEDIAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_4_x0020__inten.PA__POSTERIOR_AMYGDALAR_N: None,
                    self._nsb.burr_x0020_4_x0020__inten.CP__CAUDOPUTAMEN: None,
                    self._nsb.burr_x0020_4_x0020__inten.ACB__NUCLEUS_ACCUMBENS: None,
                    self._nsb.burr_x0020_4_x0020__inten.FS__FUNDUS_OF_STRIATUM: None,
                    self._nsb.burr_x0020_4_x0020__inten.OT__OLFACTORY_TUBERCLE: None,
                    self._nsb.burr_x0020_4_x0020__inten.L_SC__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.L_SR__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.L_SV__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.SF__SEPTOFIMBRIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.SH__SEPTOHIPPOCAMPAL_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.AAA__ANTERIOR_AMYGDALAR_A: None,
                    self._nsb.burr_x0020_4_x0020__inten.BA__BED_NUCLEUS_OF_THE_AC: None,
                    self._nsb.burr_x0020_4_x0020__inten.CEA__CENTRAL_AMYGDALAR_NU: None,
                    self._nsb.burr_x0020_4_x0020__inten.IA__INTERCALATED_AMYGDALA: None,
                    self._nsb.burr_x0020_4_x0020__inten.MEA__MEDIAL_AMYGDALAR_NUC: None,
                    self._nsb.burr_x0020_4_x0020__inten.G_PE__GLOBUS_PALLIDUS_EXT: None,
                    self._nsb.burr_x0020_4_x0020__inten.G_PI__GLOBUS_PALLIDUS_INT: None,
                    self._nsb.burr_x0020_4_x0020__inten.SI__SUBSTANTIA_INNOMINATA: None,
                    self._nsb.burr_x0020_4_x0020__inten.MA__MAGNOCELLULAR_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.MS__MEDIAL_SEPTAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.NDB__DIAGONAL_BAND_NUCLEU: None,
                    self._nsb.burr_x0020_4_x0020__inten.TRS__TRIANGULAR_NUCLEUS_O: None,
                    self._nsb.burr_x0020_4_x0020__inten.BST__BED_NUCLEI_OF_THE_ST: None,
                    self._nsb.burr_x0020_4_x0020__inten.VAL__VENTRAL_ANTERIOR_LAT: None,
                    self._nsb.burr_x0020_4_x0020__inten.VM__VENTRAL_MEDIAL_NUCLEU: None,
                    self._nsb.burr_x0020_4_x0020__inten.VPL__VENTRAL_POSTEROLATER: None,
                    self._nsb.burr_x0020_4_x0020__inten.VP_LPC__VENTRAL_POSTEROLA: None,
                    self._nsb.burr_x0020_4_x0020__inten.VPM__VENTRAL_POSTEROMEDIA: None,
                    self._nsb.burr_x0020_4_x0020__inten.VP_MPC__VENTRAL_POSTEROME: None,
                    self._nsb.burr_x0020_4_x0020__inten.PO_T__POSTERIOR_TRIANGULA: None,
                    self._nsb.burr_x0020_4_x0020__inten.SPF__SUBPARAFASCICULAR_NU: None,
                    self._nsb.burr_x0020_4_x0020__inten.SPA__SUBPARAFASCICULAR_AR: None,
                    self._nsb.burr_x0020_4_x0020__inten.PP__PERIPEDUNCULAR_NUCLEU: None,
                    self._nsb.burr_x0020_4_x0020__inten.MG__MEDIAL_GENICULATE_COM: None,
                    self._nsb.burr_x0020_4_x0020__inten.L_GD__DORSAL_PART_OF_THE: None,
                    self._nsb.burr_x0020_4_x0020__inten.LP__LATERAL_POSTERIOR_NUC: None,
                    self._nsb.burr_x0020_4_x0020__inten.PO__POSTERIOR_COMPLEX_OF: None,
                    self._nsb.burr_x0020_4_x0020__inten.POL__POSTERIOR_LIMITING_N: None,
                    self._nsb.burr_x0020_4_x0020__inten.SGN__SUPRAGENICULATE_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.ETH__ETHMOID_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_4_x0020__inten.AV__ANTEROVENTRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.AM__ANTEROMEDIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.AD__ANTERODORSAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.IAM__INTERANTEROMEDIAL_NU: None,
                    self._nsb.burr_x0020_4_x0020__inten.IAD__INTERANTERODORSAL_NU: None,
                    self._nsb.burr_x0020_4_x0020__inten.LD__LATERAL_DORSAL_NUCLEU: None,
                    self._nsb.burr_x0020_4_x0020__inten.IMD__INTERMEDIODORSAL_NUC: None,
                    self._nsb.burr_x0020_4_x0020__inten.MD__MEDIODORSAL_NUCLEUS_O: None,
                    self._nsb.burr_x0020_4_x0020__inten.SMT__SUBMEDIAL_NUCLEUS_OF: None,
                    self._nsb.burr_x0020_4_x0020__inten.PR__PERIREUNENSIS_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.PVT__PARAVENTRICULAR_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.PT__PARATAENIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.RE__NUCLEUS_OF_REUNIENS: None,
                    self._nsb.burr_x0020_4_x0020__inten.XI__XIPHOID_THALAMIC_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.RH__RHOMBOID_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.CM__CENTRAL_MEDIAL_NUCLEU: None,
                    self._nsb.burr_x0020_4_x0020__inten.PCN__PARACENTRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.CL__CENTRAL_LATERAL_NUCLE: None,
                    self._nsb.burr_x0020_4_x0020__inten.PF__PARAFASCICULAR_NUCLEU: None,
                    self._nsb.burr_x0020_4_x0020__inten.PIL__POSTERIOR_INTRALAMIN: None,
                    self._nsb.burr_x0020_4_x0020__inten.RT__RETICULAR_NUCLEUS_OF: None,
                    self._nsb.burr_x0020_4_x0020__inten.IGL__INTERGENICULATE_LEAF: None,
                    self._nsb.burr_x0020_4_x0020__inten.INT_G__INTERMEDIATE_GENIC: None,
                    self._nsb.burr_x0020_4_x0020__inten.L_GV__VENTRAL_PART_OF_THE: None,
                    self._nsb.burr_x0020_4_x0020__inten.SUB_G__SUBGENICULATE_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.MH__MEDIAL_HABENULA: None,
                    self._nsb.burr_x0020_4_x0020__inten.LH__LATERAL_HABENULA: None,
                    self._nsb.burr_x0020_4_x0020__inten.SO__SUPRAOPTIC_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.PVH__PARAVENTRICULAR_HYPO: None,
                    self._nsb.burr_x0020_4_x0020__inten.P_VA__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_4_x0020__inten.P_VI__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_4_x0020__inten.ARH__ARCUATE_HYPOTHALAMIC: None,
                    self._nsb.burr_x0020_4_x0020__inten.ADP__ANTERODORSAL_PREOPTI: None,
                    self._nsb.burr_x0020_4_x0020__inten.AVP__ANTEROVENTRAL_PREOPT: None,
                    self._nsb.burr_x0020_4_x0020__inten.AVPV__ANTEROVENTRAL_PERIV: None,
                    self._nsb.burr_x0020_4_x0020__inten.DMH__DORSOMEDIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.MEPO__MEDIAN_PREOPTIC_NUC: None,
                    self._nsb.burr_x0020_4_x0020__inten.MPO__MEDIAL_PREOPTIC_AREA: None,
                    self._nsb.burr_x0020_4_x0020__inten.PS__PARASTRIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.P_VP__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_4_x0020__inten.P_VPO__PERIVENTRICULAR_HY: None,
                    self._nsb.burr_x0020_4_x0020__inten.SBPV__SUBPARAVENTRICULAR: None,
                    self._nsb.burr_x0020_4_x0020__inten.SCH__SUPRACHIASMATIC_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.SFO__SUBFORNICAL_ORGAN: None,
                    self._nsb.burr_x0020_4_x0020__inten.VMPO__VENTROMEDIAL_PREOPT: None,
                    self._nsb.burr_x0020_4_x0020__inten.VLPO__VENTROLATERAL_PREOP: None,
                    self._nsb.burr_x0020_4_x0020__inten.AHN__ANTERIOR_HYPOTHALAMI: None,
                    self._nsb.burr_x0020_4_x0020__inten.LM__LATERAL_MAMMILLARY_NU: None,
                    self._nsb.burr_x0020_4_x0020__inten.MM__MEDIAL_MAMMILLARY_NUC: None,
                    self._nsb.burr_x0020_4_x0020__inten.SUM__SUPRAMAMMILLARY_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.TM__TUBEROMAMMILLARY_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.MPN__MEDIAL_PREOPTIC_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.P_MD__DORSAL_PREMAMMILLAR: None,
                    self._nsb.burr_x0020_4_x0020__inten.P_MV__VENTRAL_PREMAMMILLA: None,
                    self._nsb.burr_x0020_4_x0020__inten.PV_HD__PARAVENTRICULAR_HY: None,
                    self._nsb.burr_x0020_4_x0020__inten.VMH__VENTROMEDIAL_HYPOTHA: None,
                    self._nsb.burr_x0020_4_x0020__inten.PH__POSTERIOR_HYPOTHALAMI: None,
                    self._nsb.burr_x0020_4_x0020__inten.LHA__LATERAL_HYPOTHALAMIC: None,
                    self._nsb.burr_x0020_4_x0020__inten.LPO__LATERAL_PREOPTIC_ARE: None,
                    self._nsb.burr_x0020_4_x0020__inten.PSTN__PARASUBTHALAMIC_NUC: None,
                    self._nsb.burr_x0020_4_x0020__inten.PE_F__PERIFORNICAL_NUCLEU: None,
                    self._nsb.burr_x0020_4_x0020__inten.RCH__RETROCHIASMATIC_AREA: None,
                    self._nsb.burr_x0020_4_x0020__inten.STN__SUBTHALAMIC_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.TU__TUBERAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.ZI__ZONA_INCERTA: None,
                    self._nsb.burr_x0020_4_x0020__inten.S_CS__SUPERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.IC__INFERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.NB__NUCLEUS_OF_THE_BRACHI: None,
                    self._nsb.burr_x0020_4_x0020__inten.SAG__NUCLEUS_SAGULUM: None,
                    self._nsb.burr_x0020_4_x0020__inten.PBG__PARABIGEMINAL_NUCLEU: None,
                    self._nsb.burr_x0020_4_x0020__inten.S_NR__SUBSTANTIA_NIGRA_RE: None,
                    self._nsb.burr_x0020_4_x0020__inten.VTA__VENTRAL_TEGMENTAL_AR: None,
                    self._nsb.burr_x0020_4_x0020__inten.PN__PARANIGRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.RR__MIDBRAIN_RETICULAR_NU: None,
                    self._nsb.burr_x0020_4_x0020__inten.MRN__MIDBRAIN_RETICULAR_N: None,
                    self._nsb.burr_x0020_4_x0020__inten.S_CM__SUPERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.PAG__PERIAQUEDUCTAL_GRAY: None,
                    self._nsb.burr_x0020_4_x0020__inten.APN__ANTERIOR_PRETECTAL_N: None,
                    self._nsb.burr_x0020_4_x0020__inten.MPT__MEDIAL_PRETECTAL_ARE: None,
                    self._nsb.burr_x0020_4_x0020__inten.NOT__NUCLEUS_OF_THE_OPTIC: None,
                    self._nsb.burr_x0020_4_x0020__inten.NPC__NUCLEUS_OF_THE_POSTE: None,
                    self._nsb.burr_x0020_4_x0020__inten.OP__OLIVARY_PRETECTAL_NUC: None,
                    self._nsb.burr_x0020_4_x0020__inten.PPT__POSTERIOR_PRETECTAL: None,
                    self._nsb.burr_x0020_4_x0020__inten.RPF__RETROPARAFASCICULAR: None,
                    self._nsb.burr_x0020_4_x0020__inten.CUN__CUNEIFORM_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.RN__RED_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.III__OCULOMOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.MA3__MEDIAL_ACCESORY_OCUL: None,
                    self._nsb.burr_x0020_4_x0020__inten.EW__EDINGER__WESTPHAL_NUC: None,
                    self._nsb.burr_x0020_4_x0020__inten.IV__TROCHLEAR_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.PA4__PARATROCHLEAR_NUCLEU: None,
                    self._nsb.burr_x0020_4_x0020__inten.VTN__VENTRAL_TEGMENTAL_NU: None,
                    self._nsb.burr_x0020_4_x0020__inten.AT__ANTERIOR_TEGMENTAL_NU: None,
                    self._nsb.burr_x0020_4_x0020__inten.LT__LATERAL_TERMINAL_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.DT__DORSAL_TERMINAL_NUCLE: None,
                    self._nsb.burr_x0020_4_x0020__inten.MT__MEDIAL_TERMINAL_NUCLE: None,
                    self._nsb.burr_x0020_4_x0020__inten.S_NC__SUBSTANTIA_NIGRA_CO: None,
                    self._nsb.burr_x0020_4_x0020__inten.PPN__PEDUNCULOPONTINE_NUC: None,
                    self._nsb.burr_x0020_4_x0020__inten.IF__INTERFASCICULAR_NUCLE: None,
                    self._nsb.burr_x0020_4_x0020__inten.IPN__INTERPEDUNCULAR_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.RL__ROSTRAL_LINEAR_NUCLEU: None,
                    self._nsb.burr_x0020_4_x0020__inten.CLI__CENTRAL_LINEAR_NUCLE: None,
                    self._nsb.burr_x0020_4_x0020__inten.DR__DORSAL_NUCLEUS_RAPHE: None,
                    self._nsb.burr_x0020_4_x0020__inten.NLL__NUCLEUS_OF_THE_LATER: None,
                    self._nsb.burr_x0020_4_x0020__inten.PSV__PRINCIPAL_SENSORY_NU: None,
                    self._nsb.burr_x0020_4_x0020__inten.PB__PARABRACHIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.SOC__SUPERIOR_OLIVARY_COM: None,
                    self._nsb.burr_x0020_4_x0020__inten.B__BARRINGTON_S_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.DTN__DORSAL_TEGMENTAL_NUC: None,
                    self._nsb.burr_x0020_4_x0020__inten.PD_TG__POSTERODORSAL_TEGM: None,
                    self._nsb.burr_x0020_4_x0020__inten.PCG__PONTINE_CENTRAL_GRAY: None,
                    self._nsb.burr_x0020_4_x0020__inten.PG__PONTINE_GRAY: None,
                    self._nsb.burr_x0020_4_x0020__inten.PR_NC__PONTINE_RETICULAR: None,
                    self._nsb.burr_x0020_4_x0020__inten.SG__SUPRAGENUAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.SUT__SUPRATRIGEMINAL_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.TRN__TEGMENTAL_RETICULAR: None,
                    self._nsb.burr_x0020_4_x0020__inten.V__MOTOR_NUCLEUS_OF_TRIGE: None,
                    self._nsb.burr_x0020_4_x0020__inten.P5__PERITRIGEMINAL_ZONE: None,
                    self._nsb.burr_x0020_4_x0020__inten.ACS5__ACCESSORY_TRIGEMINA: None,
                    self._nsb.burr_x0020_4_x0020__inten.PC5__PARVICELLULAR_MOTOR: None,
                    self._nsb.burr_x0020_4_x0020__inten.I5__INTERTRIGEMINAL_NUCLE: None,
                    self._nsb.burr_x0020_4_x0020__inten.CS__SUPERIOR_CENTRAL_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.LC__LOCUS_CERULEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.LDT__LATERODORSAL_TEGMENT: None,
                    self._nsb.burr_x0020_4_x0020__inten.NI__NUCLEUS_INCERTUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.PR_NR__PONTINE_RETICULAR: None,
                    self._nsb.burr_x0020_4_x0020__inten.RPO__NUCLEUS_RAPHE_PONTIS: None,
                    self._nsb.burr_x0020_4_x0020__inten.SLC__SUBCERULEUS_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.SLD__SUBLATERODORSAL_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.MY__MEDULLA: None,
                    self._nsb.burr_x0020_4_x0020__inten.AP__AREA_POSTREMA: None,
                    self._nsb.burr_x0020_4_x0020__inten.DCO__DORSAL_COCHLEAR_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.VCO__VENTRAL_COCHLEAR_NUC: None,
                    self._nsb.burr_x0020_4_x0020__inten.CU__CUNEATE_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.GR__GRACILE_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.ECU__EXTERNAL_CUNEATE_NUC: None,
                    self._nsb.burr_x0020_4_x0020__inten.NTB__NUCLEUS_OF_THE_TRAPE: None,
                    self._nsb.burr_x0020_4_x0020__inten.NTS__NUCLEUS_OF_THE_SOLIT: None,
                    self._nsb.burr_x0020_4_x0020__inten.SPVC__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_4_x0020__inten.SPVI__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_4_x0020__inten.SPVO__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_4_x0020__inten.PA5__PARATRIGEMINAL_NUCLE: None,
                    self._nsb.burr_x0020_4_x0020__inten.VI__ABDUCENS_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.VII__FACIAL_MOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.AMB__NUCLEUS_AMBIGUUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.DMX__DORSAL_MOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.GRN__GIGANTOCELLULAR_RETI: None,
                    self._nsb.burr_x0020_4_x0020__inten.ICB__INFRACEREBELLAR_NUCL: None,
                    self._nsb.burr_x0020_4_x0020__inten.IO__INFERIOR_OLIVARY_COMP: None,
                    self._nsb.burr_x0020_4_x0020__inten.IRN__INTERMEDIATE_RETICUL: None,
                    self._nsb.burr_x0020_4_x0020__inten.ISN__INFERIOR_SALIVATORY: None,
                    self._nsb.burr_x0020_4_x0020__inten.LIN__LINEAR_NUCLEUS_OF_TH: None,
                    self._nsb.burr_x0020_4_x0020__inten.LRN__LATERAL_RETICULAR_NU: None,
                    self._nsb.burr_x0020_4_x0020__inten.MARN__MAGNOCELLULAR_RETIC: None,
                    self._nsb.burr_x0020_4_x0020__inten.MDRN__MEDULLARY_RETICULAR: None,
                    self._nsb.burr_x0020_4_x0020__inten.PARN__PARVICELLULAR_RETIC: None,
                    self._nsb.burr_x0020_4_x0020__inten.PAS__PARASOLITARY_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.PGRN__PARAGIGANTOCELLULAR: None,
                    self._nsb.burr_x0020_4_x0020__inten.NR__NUCLEUS_OF__ROLLER: None,
                    self._nsb.burr_x0020_4_x0020__inten.PRP__NUCLEUS_PREPOSITUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.PMR__PARAMEDIAN_RETICULAR: None,
                    self._nsb.burr_x0020_4_x0020__inten.PPY__PARAPYRAMIDAL_NUCLEU: None,
                    self._nsb.burr_x0020_4_x0020__inten.LAV__LATERAL_VESTIBULAR_N: None,
                    self._nsb.burr_x0020_4_x0020__inten.MV__MEDIAL_VESTIBULAR_NUC: None,
                    self._nsb.burr_x0020_4_x0020__inten.SPIV__SPINAL_VESTIBULAR_N: None,
                    self._nsb.burr_x0020_4_x0020__inten.SUV__SUPERIOR_VESTIBULAR: None,
                    self._nsb.burr_x0020_4_x0020__inten.X__NUCLEUS_X: None,
                    self._nsb.burr_x0020_4_x0020__inten.XII__HYPOGLOSSAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.Y__NUCLEUS_Y: None,
                    self._nsb.burr_x0020_4_x0020__inten.RM__NUCLEUS_RAPHE_MAGNUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.RPA__NUCLEUS_RAPHE_PALLID: None,
                    self._nsb.burr_x0020_4_x0020__inten.RO__NUCLEUS_RAPHE_OBSCURU: None,
                    self._nsb.burr_x0020_4_x0020__inten.LING__LINGULA_I: None,
                    self._nsb.burr_x0020_4_x0020__inten.CENT2__LOBULE_II: None,
                    self._nsb.burr_x0020_4_x0020__inten.CENT3__LOBULE_III: None,
                    self._nsb.burr_x0020_4_x0020__inten.CUL4_5__LOBULES_IV_V: None,
                    self._nsb.burr_x0020_4_x0020__inten.DEC__DECLIVE_VI: None,
                    self._nsb.burr_x0020_4_x0020__inten.FOTU__FOLIUM_TUBER_VERMIS: None,
                    self._nsb.burr_x0020_4_x0020__inten.PYR__PYRAMUS_VIII: None,
                    self._nsb.burr_x0020_4_x0020__inten.UVU__UVULA_IX: None,
                    self._nsb.burr_x0020_4_x0020__inten.NOD__NODULUS_X: None,
                    self._nsb.burr_x0020_4_x0020__inten.SIM__SIMPLE_LOBULE: None,
                    self._nsb.burr_x0020_4_x0020__inten.A_NCR1__CRUS_1: None,
                    self._nsb.burr_x0020_4_x0020__inten.A_NCR2__CRUS_2: None,
                    self._nsb.burr_x0020_4_x0020__inten.PRM__PARAMEDIAN_LOBULE: None,
                    self._nsb.burr_x0020_4_x0020__inten.COPY__COPULA_PYRAMIDIS: None,
                    self._nsb.burr_x0020_4_x0020__inten.PFL__PARAFLOCCULUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.FL__FLOCCULUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.FN__FASTIGIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.IP__INTERPOSED_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.DN__DENTATE_NUCLEUS: None,
                    self._nsb.burr_x0020_4_x0020__inten.VE_CB__VESTIBULOCEREBELLA: None,
                }.get(self._nsb.burr_x0020_4_x0020__inten, None)
            )
    
        @property
        def aind_burr_x0020_4_x0020_d_x002(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020_d_x002 to aind model."""
            return self._nsb.burr_x0020_4_x0020_d_x002

    @property
        def aind_test_x0020_1st_x0020__rou(self) -> Optional[str]:
            """Maps test_x0020_1st_x0020__rou to aind model."""
            return self._nsb.test_x0020_1st_x0020__rou

    @property
        def aind_burr_x0020_2_x0020__inten(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020__inten to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020__inten is None
                else {
                    self._nsb.burr_x0020_2_x0020__inten.FRP__FRONTAL_POLE_CEREBRA: None,
                    self._nsb.burr_x0020_2_x0020__inten.M_OP__PRIMARY_MOTOR_AREA: None,
                    self._nsb.burr_x0020_2_x0020__inten.M_OS__SECONDARY_MOTOR_ARE: None,
                    self._nsb.burr_x0020_2_x0020__inten.S_SP_N__PRIMARY_SOMATOSEN: None,
                    self._nsb.burr_x0020_2_x0020__inten.S_SP_BFD__PRIMARY_SOMATOS: None,
                    self._nsb.burr_x0020_2_x0020__inten.S_SP_LL__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_2_x0020__inten.S_SP_M__PRIMARY_SOMATOSEN: None,
                    self._nsb.burr_x0020_2_x0020__inten.S_SP_UL__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_2_x0020__inten.S_SP_TR__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_2_x0020__inten.S_SP_UN__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_2_x0020__inten.S_SS__SUPPLEMENTAL_SOMATO: None,
                    self._nsb.burr_x0020_2_x0020__inten.GU__GUSTATORY_AREAS: None,
                    self._nsb.burr_x0020_2_x0020__inten.VISC__VISCERAL_AREA: None,
                    self._nsb.burr_x0020_2_x0020__inten.AU_DD__DORSAL_AUDITORY_AR: None,
                    self._nsb.burr_x0020_2_x0020__inten.AU_DP__PRIMARY_AUDITORY_A: None,
                    self._nsb.burr_x0020_2_x0020__inten.AU_DPO__POSTERIOR_AUDITOR: None,
                    self._nsb.burr_x0020_2_x0020__inten.AU_DV__VENTRAL_AUDITORY_A: None,
                    self._nsb.burr_x0020_2_x0020__inten.VI_SAL__ANTEROLATERAL_VIS: None,
                    self._nsb.burr_x0020_2_x0020__inten.VI_SAM__ANTEROMEDIAL_VISU: None,
                    self._nsb.burr_x0020_2_x0020__inten.VI_SL__LATERAL_VISUAL_ARE: None,
                    self._nsb.burr_x0020_2_x0020__inten.VI_SP__PRIMARY_VISUAL_ARE: None,
                    self._nsb.burr_x0020_2_x0020__inten.VI_SPL__POSTEROLATERAL_VI: None,
                    self._nsb.burr_x0020_2_x0020__inten.VI_SPM_POSTEROMEDIAL_VISU: None,
                    self._nsb.burr_x0020_2_x0020__inten.VI_SLI__LATEROINTERMEDIAT: None,
                    self._nsb.burr_x0020_2_x0020__inten.VI_SPOR__POSTRHINAL_AREA: None,
                    self._nsb.burr_x0020_2_x0020__inten.AC_AD__ANTERIOR_CINGULATE: None,
                    self._nsb.burr_x0020_2_x0020__inten.AC_AV__ANTERIOR_CINGULATE: None,
                    self._nsb.burr_x0020_2_x0020__inten.PL__PRELIMBIC_AREA: None,
                    self._nsb.burr_x0020_2_x0020__inten.ILA__INFRALIMBIC_AREA: None,
                    self._nsb.burr_x0020_2_x0020__inten.OR_BL__ORBITAL_AREA_LATER: None,
                    self._nsb.burr_x0020_2_x0020__inten.OR_BM__ORBITAL_AREA_MEDIA: None,
                    self._nsb.burr_x0020_2_x0020__inten.OR_BV__ORBITAL_AREA_VENTR: None,
                    self._nsb.burr_x0020_2_x0020__inten.OR_BVL__ORBITAL_AREA_VENT: None,
                    self._nsb.burr_x0020_2_x0020__inten.A_ID__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_2_x0020__inten.A_IP__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_2_x0020__inten.A_IV__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_2_x0020__inten.RS_PAGL__RETROSPLENIAL_AR: None,
                    self._nsb.burr_x0020_2_x0020__inten.RS_PD__RETROSPLENIAL_AREA: None,
                    self._nsb.burr_x0020_2_x0020__inten.RS_PV__RETROSPLENIAL_AREA: None,
                    self._nsb.burr_x0020_2_x0020__inten.VI_SA__ANTERIOR_AREA: None,
                    self._nsb.burr_x0020_2_x0020__inten.VI_SRL__ROSTROLATERAL_VIS: None,
                    self._nsb.burr_x0020_2_x0020__inten.T_EA__TEMPORAL_ASSOCIATIO: None,
                    self._nsb.burr_x0020_2_x0020__inten.PERI__PERIRHINAL_AREA: None,
                    self._nsb.burr_x0020_2_x0020__inten.ECT__ECTORHINAL_AREA: None,
                    self._nsb.burr_x0020_2_x0020__inten.MOB__MAIN_OLFACTORY_BULB: None,
                    self._nsb.burr_x0020_2_x0020__inten.AOB__ACCESSORY_OLFACTORY: None,
                    self._nsb.burr_x0020_2_x0020__inten.AON__ANTERIOR_OLFACTORY_N: None,
                    self._nsb.burr_x0020_2_x0020__inten.T_TD__TAENIA_TECTA_DORSAL: None,
                    self._nsb.burr_x0020_2_x0020__inten.T_TV__TAENIA_TECTA_VENTRA: None,
                    self._nsb.burr_x0020_2_x0020__inten.DP__DORSAL_PEDUNCULAR_ARE: None,
                    self._nsb.burr_x0020_2_x0020__inten.PIR__PIRIFORM_AREA: None,
                    self._nsb.burr_x0020_2_x0020__inten.NLOT__NUCLEUS_OF_THE_LATE: None,
                    self._nsb.burr_x0020_2_x0020__inten.CO_AA__CORTICAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_2_x0020__inten.CO_AP__CORTICAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_2_x0020__inten.PAA__PIRIFORM_AMYGDALAR_A: None,
                    self._nsb.burr_x0020_2_x0020__inten.TR__POSTPIRIFORM_TRANSITI: None,
                    self._nsb.burr_x0020_2_x0020__inten.CA1__FIELD_CA1: None,
                    self._nsb.burr_x0020_2_x0020__inten.CA2__FIELD_CA2: None,
                    self._nsb.burr_x0020_2_x0020__inten.CA3__FIELD_CA3: None,
                    self._nsb.burr_x0020_2_x0020__inten.DG__DENTATE_GYRUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.FC__FASCIOLA_CINEREA: None,
                    self._nsb.burr_x0020_2_x0020__inten.IG__INDUSEUM_GRISEUM: None,
                    self._nsb.burr_x0020_2_x0020__inten.EN_TL__ENTORHINAL_AREA_LA: None,
                    self._nsb.burr_x0020_2_x0020__inten.EN_TM__ENTORHINAL_AREA_ME: None,
                    self._nsb.burr_x0020_2_x0020__inten.PAR__PARASUBICULUM: None,
                    self._nsb.burr_x0020_2_x0020__inten.POST__POSTSUBICULUM: None,
                    self._nsb.burr_x0020_2_x0020__inten.PRE__PRESUBICULUM: None,
                    self._nsb.burr_x0020_2_x0020__inten.SUB__SUBICULUM: None,
                    self._nsb.burr_x0020_2_x0020__inten.PRO_S__PROSUBICULUM: None,
                    self._nsb.burr_x0020_2_x0020__inten.HATA__HIPPOCAMPO_AMYGDALA: None,
                    self._nsb.burr_x0020_2_x0020__inten.A_PR__AREA_PROSTRIATA: None,
                    self._nsb.burr_x0020_2_x0020__inten.CLA__CLAUSTRUM: None,
                    self._nsb.burr_x0020_2_x0020__inten.E_PD__ENDOPIRIFORM_NUCLEU: None,
                    self._nsb.burr_x0020_2_x0020__inten.E_PV__ENDOPIRIFORM_NUCLEU: None,
                    self._nsb.burr_x0020_2_x0020__inten.LA__LATERAL_AMYGDALAR_NUC: None,
                    self._nsb.burr_x0020_2_x0020__inten.BLA__BASOLATERAL_AMYGDALA: None,
                    self._nsb.burr_x0020_2_x0020__inten.BMA__BASOMEDIAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_2_x0020__inten.PA__POSTERIOR_AMYGDALAR_N: None,
                    self._nsb.burr_x0020_2_x0020__inten.CP__CAUDOPUTAMEN: None,
                    self._nsb.burr_x0020_2_x0020__inten.ACB__NUCLEUS_ACCUMBENS: None,
                    self._nsb.burr_x0020_2_x0020__inten.FS__FUNDUS_OF_STRIATUM: None,
                    self._nsb.burr_x0020_2_x0020__inten.OT__OLFACTORY_TUBERCLE: None,
                    self._nsb.burr_x0020_2_x0020__inten.L_SC__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.L_SR__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.L_SV__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.SF__SEPTOFIMBRIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.SH__SEPTOHIPPOCAMPAL_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.AAA__ANTERIOR_AMYGDALAR_A: None,
                    self._nsb.burr_x0020_2_x0020__inten.BA__BED_NUCLEUS_OF_THE_AC: None,
                    self._nsb.burr_x0020_2_x0020__inten.CEA__CENTRAL_AMYGDALAR_NU: None,
                    self._nsb.burr_x0020_2_x0020__inten.IA__INTERCALATED_AMYGDALA: None,
                    self._nsb.burr_x0020_2_x0020__inten.MEA__MEDIAL_AMYGDALAR_NUC: None,
                    self._nsb.burr_x0020_2_x0020__inten.G_PE__GLOBUS_PALLIDUS_EXT: None,
                    self._nsb.burr_x0020_2_x0020__inten.G_PI__GLOBUS_PALLIDUS_INT: None,
                    self._nsb.burr_x0020_2_x0020__inten.SI__SUBSTANTIA_INNOMINATA: None,
                    self._nsb.burr_x0020_2_x0020__inten.MA__MAGNOCELLULAR_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.MS__MEDIAL_SEPTAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.NDB__DIAGONAL_BAND_NUCLEU: None,
                    self._nsb.burr_x0020_2_x0020__inten.TRS__TRIANGULAR_NUCLEUS_O: None,
                    self._nsb.burr_x0020_2_x0020__inten.BST__BED_NUCLEI_OF_THE_ST: None,
                    self._nsb.burr_x0020_2_x0020__inten.VAL__VENTRAL_ANTERIOR_LAT: None,
                    self._nsb.burr_x0020_2_x0020__inten.VM__VENTRAL_MEDIAL_NUCLEU: None,
                    self._nsb.burr_x0020_2_x0020__inten.VPL__VENTRAL_POSTEROLATER: None,
                    self._nsb.burr_x0020_2_x0020__inten.VP_LPC__VENTRAL_POSTEROLA: None,
                    self._nsb.burr_x0020_2_x0020__inten.VPM__VENTRAL_POSTEROMEDIA: None,
                    self._nsb.burr_x0020_2_x0020__inten.VP_MPC__VENTRAL_POSTEROME: None,
                    self._nsb.burr_x0020_2_x0020__inten.PO_T__POSTERIOR_TRIANGULA: None,
                    self._nsb.burr_x0020_2_x0020__inten.SPF__SUBPARAFASCICULAR_NU: None,
                    self._nsb.burr_x0020_2_x0020__inten.SPA__SUBPARAFASCICULAR_AR: None,
                    self._nsb.burr_x0020_2_x0020__inten.PP__PERIPEDUNCULAR_NUCLEU: None,
                    self._nsb.burr_x0020_2_x0020__inten.MG__MEDIAL_GENICULATE_COM: None,
                    self._nsb.burr_x0020_2_x0020__inten.L_GD__DORSAL_PART_OF_THE: None,
                    self._nsb.burr_x0020_2_x0020__inten.LP__LATERAL_POSTERIOR_NUC: None,
                    self._nsb.burr_x0020_2_x0020__inten.PO__POSTERIOR_COMPLEX_OF: None,
                    self._nsb.burr_x0020_2_x0020__inten.POL__POSTERIOR_LIMITING_N: None,
                    self._nsb.burr_x0020_2_x0020__inten.SGN__SUPRAGENICULATE_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.ETH__ETHMOID_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_2_x0020__inten.AV__ANTEROVENTRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.AM__ANTEROMEDIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.AD__ANTERODORSAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.IAM__INTERANTEROMEDIAL_NU: None,
                    self._nsb.burr_x0020_2_x0020__inten.IAD__INTERANTERODORSAL_NU: None,
                    self._nsb.burr_x0020_2_x0020__inten.LD__LATERAL_DORSAL_NUCLEU: None,
                    self._nsb.burr_x0020_2_x0020__inten.IMD__INTERMEDIODORSAL_NUC: None,
                    self._nsb.burr_x0020_2_x0020__inten.MD__MEDIODORSAL_NUCLEUS_O: None,
                    self._nsb.burr_x0020_2_x0020__inten.SMT__SUBMEDIAL_NUCLEUS_OF: None,
                    self._nsb.burr_x0020_2_x0020__inten.PR__PERIREUNENSIS_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.PVT__PARAVENTRICULAR_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.PT__PARATAENIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.RE__NUCLEUS_OF_REUNIENS: None,
                    self._nsb.burr_x0020_2_x0020__inten.XI__XIPHOID_THALAMIC_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.RH__RHOMBOID_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.CM__CENTRAL_MEDIAL_NUCLEU: None,
                    self._nsb.burr_x0020_2_x0020__inten.PCN__PARACENTRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.CL__CENTRAL_LATERAL_NUCLE: None,
                    self._nsb.burr_x0020_2_x0020__inten.PF__PARAFASCICULAR_NUCLEU: None,
                    self._nsb.burr_x0020_2_x0020__inten.PIL__POSTERIOR_INTRALAMIN: None,
                    self._nsb.burr_x0020_2_x0020__inten.RT__RETICULAR_NUCLEUS_OF: None,
                    self._nsb.burr_x0020_2_x0020__inten.IGL__INTERGENICULATE_LEAF: None,
                    self._nsb.burr_x0020_2_x0020__inten.INT_G__INTERMEDIATE_GENIC: None,
                    self._nsb.burr_x0020_2_x0020__inten.L_GV__VENTRAL_PART_OF_THE: None,
                    self._nsb.burr_x0020_2_x0020__inten.SUB_G__SUBGENICULATE_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.MH__MEDIAL_HABENULA: None,
                    self._nsb.burr_x0020_2_x0020__inten.LH__LATERAL_HABENULA: None,
                    self._nsb.burr_x0020_2_x0020__inten.SO__SUPRAOPTIC_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.PVH__PARAVENTRICULAR_HYPO: None,
                    self._nsb.burr_x0020_2_x0020__inten.P_VA__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_2_x0020__inten.P_VI__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_2_x0020__inten.ARH__ARCUATE_HYPOTHALAMIC: None,
                    self._nsb.burr_x0020_2_x0020__inten.ADP__ANTERODORSAL_PREOPTI: None,
                    self._nsb.burr_x0020_2_x0020__inten.AVP__ANTEROVENTRAL_PREOPT: None,
                    self._nsb.burr_x0020_2_x0020__inten.AVPV__ANTEROVENTRAL_PERIV: None,
                    self._nsb.burr_x0020_2_x0020__inten.DMH__DORSOMEDIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.MEPO__MEDIAN_PREOPTIC_NUC: None,
                    self._nsb.burr_x0020_2_x0020__inten.MPO__MEDIAL_PREOPTIC_AREA: None,
                    self._nsb.burr_x0020_2_x0020__inten.PS__PARASTRIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.P_VP__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_2_x0020__inten.P_VPO__PERIVENTRICULAR_HY: None,
                    self._nsb.burr_x0020_2_x0020__inten.SBPV__SUBPARAVENTRICULAR: None,
                    self._nsb.burr_x0020_2_x0020__inten.SCH__SUPRACHIASMATIC_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.SFO__SUBFORNICAL_ORGAN: None,
                    self._nsb.burr_x0020_2_x0020__inten.VMPO__VENTROMEDIAL_PREOPT: None,
                    self._nsb.burr_x0020_2_x0020__inten.VLPO__VENTROLATERAL_PREOP: None,
                    self._nsb.burr_x0020_2_x0020__inten.AHN__ANTERIOR_HYPOTHALAMI: None,
                    self._nsb.burr_x0020_2_x0020__inten.LM__LATERAL_MAMMILLARY_NU: None,
                    self._nsb.burr_x0020_2_x0020__inten.MM__MEDIAL_MAMMILLARY_NUC: None,
                    self._nsb.burr_x0020_2_x0020__inten.SUM__SUPRAMAMMILLARY_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.TM__TUBEROMAMMILLARY_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.MPN__MEDIAL_PREOPTIC_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.P_MD__DORSAL_PREMAMMILLAR: None,
                    self._nsb.burr_x0020_2_x0020__inten.P_MV__VENTRAL_PREMAMMILLA: None,
                    self._nsb.burr_x0020_2_x0020__inten.PV_HD__PARAVENTRICULAR_HY: None,
                    self._nsb.burr_x0020_2_x0020__inten.VMH__VENTROMEDIAL_HYPOTHA: None,
                    self._nsb.burr_x0020_2_x0020__inten.PH__POSTERIOR_HYPOTHALAMI: None,
                    self._nsb.burr_x0020_2_x0020__inten.LHA__LATERAL_HYPOTHALAMIC: None,
                    self._nsb.burr_x0020_2_x0020__inten.LPO__LATERAL_PREOPTIC_ARE: None,
                    self._nsb.burr_x0020_2_x0020__inten.PSTN__PARASUBTHALAMIC_NUC: None,
                    self._nsb.burr_x0020_2_x0020__inten.PE_F__PERIFORNICAL_NUCLEU: None,
                    self._nsb.burr_x0020_2_x0020__inten.RCH__RETROCHIASMATIC_AREA: None,
                    self._nsb.burr_x0020_2_x0020__inten.STN__SUBTHALAMIC_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.TU__TUBERAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.ZI__ZONA_INCERTA: None,
                    self._nsb.burr_x0020_2_x0020__inten.S_CS__SUPERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.IC__INFERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.NB__NUCLEUS_OF_THE_BRACHI: None,
                    self._nsb.burr_x0020_2_x0020__inten.SAG__NUCLEUS_SAGULUM: None,
                    self._nsb.burr_x0020_2_x0020__inten.PBG__PARABIGEMINAL_NUCLEU: None,
                    self._nsb.burr_x0020_2_x0020__inten.S_NR__SUBSTANTIA_NIGRA_RE: None,
                    self._nsb.burr_x0020_2_x0020__inten.VTA__VENTRAL_TEGMENTAL_AR: None,
                    self._nsb.burr_x0020_2_x0020__inten.PN__PARANIGRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.RR__MIDBRAIN_RETICULAR_NU: None,
                    self._nsb.burr_x0020_2_x0020__inten.MRN__MIDBRAIN_RETICULAR_N: None,
                    self._nsb.burr_x0020_2_x0020__inten.S_CM__SUPERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.PAG__PERIAQUEDUCTAL_GRAY: None,
                    self._nsb.burr_x0020_2_x0020__inten.APN__ANTERIOR_PRETECTAL_N: None,
                    self._nsb.burr_x0020_2_x0020__inten.MPT__MEDIAL_PRETECTAL_ARE: None,
                    self._nsb.burr_x0020_2_x0020__inten.NOT__NUCLEUS_OF_THE_OPTIC: None,
                    self._nsb.burr_x0020_2_x0020__inten.NPC__NUCLEUS_OF_THE_POSTE: None,
                    self._nsb.burr_x0020_2_x0020__inten.OP__OLIVARY_PRETECTAL_NUC: None,
                    self._nsb.burr_x0020_2_x0020__inten.PPT__POSTERIOR_PRETECTAL: None,
                    self._nsb.burr_x0020_2_x0020__inten.RPF__RETROPARAFASCICULAR: None,
                    self._nsb.burr_x0020_2_x0020__inten.CUN__CUNEIFORM_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.RN__RED_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.III__OCULOMOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.MA3__MEDIAL_ACCESORY_OCUL: None,
                    self._nsb.burr_x0020_2_x0020__inten.EW__EDINGER__WESTPHAL_NUC: None,
                    self._nsb.burr_x0020_2_x0020__inten.IV__TROCHLEAR_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.PA4__PARATROCHLEAR_NUCLEU: None,
                    self._nsb.burr_x0020_2_x0020__inten.VTN__VENTRAL_TEGMENTAL_NU: None,
                    self._nsb.burr_x0020_2_x0020__inten.AT__ANTERIOR_TEGMENTAL_NU: None,
                    self._nsb.burr_x0020_2_x0020__inten.LT__LATERAL_TERMINAL_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.DT__DORSAL_TERMINAL_NUCLE: None,
                    self._nsb.burr_x0020_2_x0020__inten.MT__MEDIAL_TERMINAL_NUCLE: None,
                    self._nsb.burr_x0020_2_x0020__inten.S_NC__SUBSTANTIA_NIGRA_CO: None,
                    self._nsb.burr_x0020_2_x0020__inten.PPN__PEDUNCULOPONTINE_NUC: None,
                    self._nsb.burr_x0020_2_x0020__inten.IF__INTERFASCICULAR_NUCLE: None,
                    self._nsb.burr_x0020_2_x0020__inten.IPN__INTERPEDUNCULAR_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.RL__ROSTRAL_LINEAR_NUCLEU: None,
                    self._nsb.burr_x0020_2_x0020__inten.CLI__CENTRAL_LINEAR_NUCLE: None,
                    self._nsb.burr_x0020_2_x0020__inten.DR__DORSAL_NUCLEUS_RAPHE: None,
                    self._nsb.burr_x0020_2_x0020__inten.NLL__NUCLEUS_OF_THE_LATER: None,
                    self._nsb.burr_x0020_2_x0020__inten.PSV__PRINCIPAL_SENSORY_NU: None,
                    self._nsb.burr_x0020_2_x0020__inten.PB__PARABRACHIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.SOC__SUPERIOR_OLIVARY_COM: None,
                    self._nsb.burr_x0020_2_x0020__inten.B__BARRINGTON_S_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.DTN__DORSAL_TEGMENTAL_NUC: None,
                    self._nsb.burr_x0020_2_x0020__inten.PD_TG__POSTERODORSAL_TEGM: None,
                    self._nsb.burr_x0020_2_x0020__inten.PCG__PONTINE_CENTRAL_GRAY: None,
                    self._nsb.burr_x0020_2_x0020__inten.PG__PONTINE_GRAY: None,
                    self._nsb.burr_x0020_2_x0020__inten.PR_NC__PONTINE_RETICULAR: None,
                    self._nsb.burr_x0020_2_x0020__inten.SG__SUPRAGENUAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.SUT__SUPRATRIGEMINAL_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.TRN__TEGMENTAL_RETICULAR: None,
                    self._nsb.burr_x0020_2_x0020__inten.V__MOTOR_NUCLEUS_OF_TRIGE: None,
                    self._nsb.burr_x0020_2_x0020__inten.P5__PERITRIGEMINAL_ZONE: None,
                    self._nsb.burr_x0020_2_x0020__inten.ACS5__ACCESSORY_TRIGEMINA: None,
                    self._nsb.burr_x0020_2_x0020__inten.PC5__PARVICELLULAR_MOTOR: None,
                    self._nsb.burr_x0020_2_x0020__inten.I5__INTERTRIGEMINAL_NUCLE: None,
                    self._nsb.burr_x0020_2_x0020__inten.CS__SUPERIOR_CENTRAL_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.LC__LOCUS_CERULEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.LDT__LATERODORSAL_TEGMENT: None,
                    self._nsb.burr_x0020_2_x0020__inten.NI__NUCLEUS_INCERTUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.PR_NR__PONTINE_RETICULAR: None,
                    self._nsb.burr_x0020_2_x0020__inten.RPO__NUCLEUS_RAPHE_PONTIS: None,
                    self._nsb.burr_x0020_2_x0020__inten.SLC__SUBCERULEUS_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.SLD__SUBLATERODORSAL_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.MY__MEDULLA: None,
                    self._nsb.burr_x0020_2_x0020__inten.AP__AREA_POSTREMA: None,
                    self._nsb.burr_x0020_2_x0020__inten.DCO__DORSAL_COCHLEAR_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.VCO__VENTRAL_COCHLEAR_NUC: None,
                    self._nsb.burr_x0020_2_x0020__inten.CU__CUNEATE_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.GR__GRACILE_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.ECU__EXTERNAL_CUNEATE_NUC: None,
                    self._nsb.burr_x0020_2_x0020__inten.NTB__NUCLEUS_OF_THE_TRAPE: None,
                    self._nsb.burr_x0020_2_x0020__inten.NTS__NUCLEUS_OF_THE_SOLIT: None,
                    self._nsb.burr_x0020_2_x0020__inten.SPVC__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_2_x0020__inten.SPVI__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_2_x0020__inten.SPVO__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_2_x0020__inten.PA5__PARATRIGEMINAL_NUCLE: None,
                    self._nsb.burr_x0020_2_x0020__inten.VI__ABDUCENS_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.VII__FACIAL_MOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.AMB__NUCLEUS_AMBIGUUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.DMX__DORSAL_MOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.GRN__GIGANTOCELLULAR_RETI: None,
                    self._nsb.burr_x0020_2_x0020__inten.ICB__INFRACEREBELLAR_NUCL: None,
                    self._nsb.burr_x0020_2_x0020__inten.IO__INFERIOR_OLIVARY_COMP: None,
                    self._nsb.burr_x0020_2_x0020__inten.IRN__INTERMEDIATE_RETICUL: None,
                    self._nsb.burr_x0020_2_x0020__inten.ISN__INFERIOR_SALIVATORY: None,
                    self._nsb.burr_x0020_2_x0020__inten.LIN__LINEAR_NUCLEUS_OF_TH: None,
                    self._nsb.burr_x0020_2_x0020__inten.LRN__LATERAL_RETICULAR_NU: None,
                    self._nsb.burr_x0020_2_x0020__inten.MARN__MAGNOCELLULAR_RETIC: None,
                    self._nsb.burr_x0020_2_x0020__inten.MDRN__MEDULLARY_RETICULAR: None,
                    self._nsb.burr_x0020_2_x0020__inten.PARN__PARVICELLULAR_RETIC: None,
                    self._nsb.burr_x0020_2_x0020__inten.PAS__PARASOLITARY_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.PGRN__PARAGIGANTOCELLULAR: None,
                    self._nsb.burr_x0020_2_x0020__inten.NR__NUCLEUS_OF__ROLLER: None,
                    self._nsb.burr_x0020_2_x0020__inten.PRP__NUCLEUS_PREPOSITUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.PMR__PARAMEDIAN_RETICULAR: None,
                    self._nsb.burr_x0020_2_x0020__inten.PPY__PARAPYRAMIDAL_NUCLEU: None,
                    self._nsb.burr_x0020_2_x0020__inten.LAV__LATERAL_VESTIBULAR_N: None,
                    self._nsb.burr_x0020_2_x0020__inten.MV__MEDIAL_VESTIBULAR_NUC: None,
                    self._nsb.burr_x0020_2_x0020__inten.SPIV__SPINAL_VESTIBULAR_N: None,
                    self._nsb.burr_x0020_2_x0020__inten.SUV__SUPERIOR_VESTIBULAR: None,
                    self._nsb.burr_x0020_2_x0020__inten.X__NUCLEUS_X: None,
                    self._nsb.burr_x0020_2_x0020__inten.XII__HYPOGLOSSAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.Y__NUCLEUS_Y: None,
                    self._nsb.burr_x0020_2_x0020__inten.RM__NUCLEUS_RAPHE_MAGNUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.RPA__NUCLEUS_RAPHE_PALLID: None,
                    self._nsb.burr_x0020_2_x0020__inten.RO__NUCLEUS_RAPHE_OBSCURU: None,
                    self._nsb.burr_x0020_2_x0020__inten.LING__LINGULA_I: None,
                    self._nsb.burr_x0020_2_x0020__inten.CENT2__LOBULE_II: None,
                    self._nsb.burr_x0020_2_x0020__inten.CENT3__LOBULE_III: None,
                    self._nsb.burr_x0020_2_x0020__inten.CUL4_5__LOBULES_IV_V: None,
                    self._nsb.burr_x0020_2_x0020__inten.DEC__DECLIVE_VI: None,
                    self._nsb.burr_x0020_2_x0020__inten.FOTU__FOLIUM_TUBER_VERMIS: None,
                    self._nsb.burr_x0020_2_x0020__inten.PYR__PYRAMUS_VIII: None,
                    self._nsb.burr_x0020_2_x0020__inten.UVU__UVULA_IX: None,
                    self._nsb.burr_x0020_2_x0020__inten.NOD__NODULUS_X: None,
                    self._nsb.burr_x0020_2_x0020__inten.SIM__SIMPLE_LOBULE: None,
                    self._nsb.burr_x0020_2_x0020__inten.A_NCR1__CRUS_1: None,
                    self._nsb.burr_x0020_2_x0020__inten.A_NCR2__CRUS_2: None,
                    self._nsb.burr_x0020_2_x0020__inten.PRM__PARAMEDIAN_LOBULE: None,
                    self._nsb.burr_x0020_2_x0020__inten.COPY__COPULA_PYRAMIDIS: None,
                    self._nsb.burr_x0020_2_x0020__inten.PFL__PARAFLOCCULUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.FL__FLOCCULUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.FN__FASTIGIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.IP__INTERPOSED_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.DN__DENTATE_NUCLEUS: None,
                    self._nsb.burr_x0020_2_x0020__inten.VE_CB__VESTIBULOCEREBELLA: None,
                }.get(self._nsb.burr_x0020_2_x0020__inten, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020__spina(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020__spina to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020__spina is None
                else {
                    self._nsb.burr_x0020_2_x0020__spina.SELECT: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_C1_C2: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_C2_C3: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_C3_C4: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_C4_C5: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_C6_C7: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_C7_C8: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_C8_T1: None,
                    self._nsb.burr_x0020_2_x0020__spina.BETWEEN_T1_T2: None,
                }.get(self._nsb.burr_x0020_2_x0020__spina, None)
            )
    
        @property
        def aind_burr_x0020_2_x0020_d_x002(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020_d_x002 to aind model."""
            return self._nsb.burr_x0020_2_x0020_d_x002

    @property
        def aind_burr_x0020_5_x0020__injec_003(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__injec_003 to aind model."""
            return self._nsb.burr_x0020_5_x0020__injec_003

    @property
        def aind_burr_x0020_1_x0020__injec_001(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__injec_001 to aind model."""
            return self._nsb.burr_x0020_1_x0020__injec_001

    @property
        def aind_burr_x0020_3_x0020__injec_005(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__injec_005 to aind model."""
            return self._nsb.burr_x0020_3_x0020__injec_005

    @property
        def aind_burr_x0020_2_x0020__injec_005(self) -> Optional[str]:
            """Maps burr_x0020_2_x0020__injec_005 to aind model."""
            return self._nsb.burr_x0020_2_x0020__injec_005

    @property
        def aind_burr_x0020_4_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_4_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_4_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_4_x0020__fiber.STANDARD__PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_4_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_4_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_4_x0020__hemis(self) -> Optional[Any]:
            """Maps burr_x0020_4_x0020__hemis to aind model."""
            return (
                None
                if self._nsb.burr_x0020_4_x0020__hemis is None
                else {
                    self._nsb.burr_x0020_4_x0020__hemis.SELECT: None,
                    self._nsb.burr_x0020_4_x0020__hemis.LEFT: None,
                    self._nsb.burr_x0020_4_x0020__hemis.RIGHT: None,
                }.get(self._nsb.burr_x0020_4_x0020__hemis, None)
            )
    
        @property
        def aind_burr_x0020_4_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__injec to aind model."""
            return self._nsb.burr_x0020_4_x0020__injec

    @property
        def aind_burr_x0020_3_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__angle to aind model."""
            return self._nsb.burr_x0020_3_x0020__angle

    @property
        def aind_burr3_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr3_x0020_a_x002f_p to aind model."""
            return self._nsb.burr3_x0020_a_x002f_p

    @property
        def aind_burr4_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr4_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr4_x0020__injection_x0 is None
                else {
                    self._nsb.burr4_x0020__injection_x0.SELECT: None,
                    self._nsb.burr4_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr4_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr4_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr4_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr4_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr4_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr4_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr4_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr4_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr4_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr4_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr4_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr4_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr4_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr4_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr4_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr4_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr4_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr4_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr4_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr4_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr4_x0020__perform_x002 is None
                else {
                    self._nsb.burr4_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr4_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr4_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr4_x0020__status(self) -> Optional[Any]:
            """Maps burr4_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr4_x0020__status is None
                else {
                    self._nsb.burr4_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr4_x0020__status, None)
            )
    
        @property
        def aind_burr4_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr4_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr4_x0020__virus_x0020 is None
                else {
                    self._nsb.burr4_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr4_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr4_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr4_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr4_x0020_a_x002f_p to aind model."""
            return self._nsb.burr4_x0020_a_x002f_p

    @property
        def aind_burr_x0020_5_x0020__injec_001(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__injec_001 to aind model."""
            return self._nsb.burr_x0020_5_x0020__injec_001

    @property
        def aind_virus_x0020_d_x002f_v(self) -> Optional[str]:
            """Maps virus_x0020_d_x002f_v to aind model."""
            return self._nsb.virus_x0020_d_x002f_v

    @property
        def aind_app_editor(self) -> Optional[str]:
            """Maps app_editor to aind model."""
            return self._nsb.app_editor

    @property
        def aind_burr1_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr1_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr1_x0020__perform_x002 is None
                else {
                    self._nsb.burr1_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr1_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr1_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr1_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr1_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr1_x0020__virus_x0020 is None
                else {
                    self._nsb.burr1_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr1_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr1_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr2_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr2_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__injection_x0 is None
                else {
                    self._nsb.burr2_x0020__injection_x0.SELECT: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr2_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr2_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr2_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr2_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr2_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__perform_x002 is None
                else {
                    self._nsb.burr2_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr2_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr2_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr2_x0020__status(self) -> Optional[Any]:
            """Maps burr2_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__status is None
                else {
                    self._nsb.burr2_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr2_x0020__status, None)
            )
    
        @property
        def aind_burr2_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr2_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr2_x0020__virus_x0020 is None
                else {
                    self._nsb.burr2_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr2_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr2_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr3_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__injection_x0 is None
                else {
                    self._nsb.burr3_x0020__injection_x0.SELECT: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr3_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr3_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr3_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr3_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr3_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__perform_x002 is None
                else {
                    self._nsb.burr3_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr3_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr3_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr3_x0020__status(self) -> Optional[Any]:
            """Maps burr3_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__status is None
                else {
                    self._nsb.burr3_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr3_x0020__status, None)
            )
    
        @property
        def aind_burr3_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr3_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr3_x0020__virus_x0020 is None
                else {
                    self._nsb.burr3_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr3_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr3_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr3_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr3_x0020_a_x002f_p to aind model."""
            return self._nsb.burr3_x0020_a_x002f_p

    @property
        def aind_burr_x0020_2_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_2_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_2_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_2_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_2_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_2_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_3_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__angle to aind model."""
            return self._nsb.burr_x0020_3_x0020__angle

    @property
        def aind_burr4_x0020_a_x002f_p(self) -> Optional[str]:
            """Maps burr4_x0020_a_x002f_p to aind model."""
            return self._nsb.burr4_x0020_a_x002f_p

    @property
        def aind_burr_x0020_4_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_4_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_4_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_4_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_4_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_4_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020__angle(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020__angle to aind model."""
            return self._nsb.burr_x0020_5_x0020__angle

    @property
        def aind_burr_x0020_3_x0020__injec_003(self) -> Optional[str]:
            """Maps burr_x0020_3_x0020__injec_003 to aind model."""
            return self._nsb.burr_x0020_3_x0020__injec_003

    @property
        def aind_burr_x0020_6_x0020__injec(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020__injec to aind model."""
            return self._nsb.burr_x0020_6_x0020__injec

    @property
        def aind_date_x0020_of_x0020__surg(self) -> Optional[str]:
            """Maps date_x0020_of_x0020__surg to aind model."""
            return self._nsb.date_x0020_of_x0020__surg

    @property
        def aind_behavior_x0020__platform(self) -> Optional[Any]:
            """Maps behavior_x0020__platform to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__platform is None
                else {
                    self._nsb.behavior_x0020__platform.MINDSCOPE: None,
                    self._nsb.behavior_x0020__platform.FORAGING: None,
                    self._nsb.behavior_x0020__platform.VR: None,
                }.get(self._nsb.behavior_x0020__platform, None)
            )
    
        @property
        def aind_behavior_x0020__type(self) -> Optional[Any]:
            """Maps behavior_x0020__type to aind model."""
            return (
                None
                if self._nsb.behavior_x0020__type is None
                else {
                    self._nsb.behavior_x0020__type.SELECT: None,
                    self._nsb.behavior_x0020__type.FORAGING: None,
                    self._nsb.behavior_x0020__type.FORAGING_FP: None,
                    self._nsb.behavior_x0020__type.WR__HAB: None,
                    self._nsb.behavior_x0020__type.HAB__ONLY: None,
                }.get(self._nsb.behavior_x0020__type, None)
            )
    
        @property
        def aind_behavior_x0020_fip_x0020(self) -> Optional[Any]:
            """Maps behavior_x0020_fip_x0020 to aind model."""
            return (
                None
                if self._nsb.behavior_x0020_fip_x0020 is None
                else {
                    self._nsb.behavior_x0020_fip_x0020.N_A: None,
                    self._nsb.behavior_x0020_fip_x0020.NORMAL: None,
                    self._nsb.behavior_x0020_fip_x0020.AXON: None,
                }.get(self._nsb.behavior_x0020_fip_x0020, None)
            )
    
        @property
        def aind_black_x0020__cement(self) -> Optional[Any]:
            """Maps black_x0020__cement to aind model."""
            return (
                None
                if self._nsb.black_x0020__cement is None
                else {
                    self._nsb.black_x0020__cement.YES: None,
                    self._nsb.black_x0020__cement.NO: None,
                }.get(self._nsb.black_x0020__cement, None)
            )
    
        @property
        def aind_breg2_lamb(self) -> Optional[str]:
            """Maps breg2_lamb to aind model."""
            return self._nsb.breg2_lamb

    @property
        def aind_burr_x0020_6_x0020__inten(self) -> Optional[Any]:
            """Maps burr_x0020_6_x0020__inten to aind model."""
            return (
                None
                if self._nsb.burr_x0020_6_x0020__inten is None
                else {
                    self._nsb.burr_x0020_6_x0020__inten.FRP__FRONTAL_POLE_CEREBRA: None,
                    self._nsb.burr_x0020_6_x0020__inten.M_OP__PRIMARY_MOTOR_AREA: None,
                    self._nsb.burr_x0020_6_x0020__inten.M_OS__SECONDARY_MOTOR_ARE: None,
                    self._nsb.burr_x0020_6_x0020__inten.S_SP_N__PRIMARY_SOMATOSEN: None,
                    self._nsb.burr_x0020_6_x0020__inten.S_SP_BFD__PRIMARY_SOMATOS: None,
                    self._nsb.burr_x0020_6_x0020__inten.S_SP_LL__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_6_x0020__inten.S_SP_M__PRIMARY_SOMATOSEN: None,
                    self._nsb.burr_x0020_6_x0020__inten.S_SP_UL__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_6_x0020__inten.S_SP_TR__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_6_x0020__inten.S_SP_UN__PRIMARY_SOMATOSE: None,
                    self._nsb.burr_x0020_6_x0020__inten.S_SS__SUPPLEMENTAL_SOMATO: None,
                    self._nsb.burr_x0020_6_x0020__inten.GU__GUSTATORY_AREAS: None,
                    self._nsb.burr_x0020_6_x0020__inten.VISC__VISCERAL_AREA: None,
                    self._nsb.burr_x0020_6_x0020__inten.AU_DD__DORSAL_AUDITORY_AR: None,
                    self._nsb.burr_x0020_6_x0020__inten.AU_DP__PRIMARY_AUDITORY_A: None,
                    self._nsb.burr_x0020_6_x0020__inten.AU_DPO__POSTERIOR_AUDITOR: None,
                    self._nsb.burr_x0020_6_x0020__inten.AU_DV__VENTRAL_AUDITORY_A: None,
                    self._nsb.burr_x0020_6_x0020__inten.VI_SAL__ANTEROLATERAL_VIS: None,
                    self._nsb.burr_x0020_6_x0020__inten.VI_SAM__ANTEROMEDIAL_VISU: None,
                    self._nsb.burr_x0020_6_x0020__inten.VI_SL__LATERAL_VISUAL_ARE: None,
                    self._nsb.burr_x0020_6_x0020__inten.VI_SP__PRIMARY_VISUAL_ARE: None,
                    self._nsb.burr_x0020_6_x0020__inten.VI_SPL__POSTEROLATERAL_VI: None,
                    self._nsb.burr_x0020_6_x0020__inten.VI_SPM_POSTEROMEDIAL_VISU: None,
                    self._nsb.burr_x0020_6_x0020__inten.VI_SLI__LATEROINTERMEDIAT: None,
                    self._nsb.burr_x0020_6_x0020__inten.VI_SPOR__POSTRHINAL_AREA: None,
                    self._nsb.burr_x0020_6_x0020__inten.AC_AD__ANTERIOR_CINGULATE: None,
                    self._nsb.burr_x0020_6_x0020__inten.AC_AV__ANTERIOR_CINGULATE: None,
                    self._nsb.burr_x0020_6_x0020__inten.PL__PRELIMBIC_AREA: None,
                    self._nsb.burr_x0020_6_x0020__inten.ILA__INFRALIMBIC_AREA: None,
                    self._nsb.burr_x0020_6_x0020__inten.OR_BL__ORBITAL_AREA_LATER: None,
                    self._nsb.burr_x0020_6_x0020__inten.OR_BM__ORBITAL_AREA_MEDIA: None,
                    self._nsb.burr_x0020_6_x0020__inten.OR_BV__ORBITAL_AREA_VENTR: None,
                    self._nsb.burr_x0020_6_x0020__inten.OR_BVL__ORBITAL_AREA_VENT: None,
                    self._nsb.burr_x0020_6_x0020__inten.A_ID__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_6_x0020__inten.A_IP__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_6_x0020__inten.A_IV__AGRANULAR_INSULAR_A: None,
                    self._nsb.burr_x0020_6_x0020__inten.RS_PAGL__RETROSPLENIAL_AR: None,
                    self._nsb.burr_x0020_6_x0020__inten.RS_PD__RETROSPLENIAL_AREA: None,
                    self._nsb.burr_x0020_6_x0020__inten.RS_PV__RETROSPLENIAL_AREA: None,
                    self._nsb.burr_x0020_6_x0020__inten.VI_SA__ANTERIOR_AREA: None,
                    self._nsb.burr_x0020_6_x0020__inten.VI_SRL__ROSTROLATERAL_VIS: None,
                    self._nsb.burr_x0020_6_x0020__inten.T_EA__TEMPORAL_ASSOCIATIO: None,
                    self._nsb.burr_x0020_6_x0020__inten.PERI__PERIRHINAL_AREA: None,
                    self._nsb.burr_x0020_6_x0020__inten.ECT__ECTORHINAL_AREA: None,
                    self._nsb.burr_x0020_6_x0020__inten.MOB__MAIN_OLFACTORY_BULB: None,
                    self._nsb.burr_x0020_6_x0020__inten.AOB__ACCESSORY_OLFACTORY: None,
                    self._nsb.burr_x0020_6_x0020__inten.AON__ANTERIOR_OLFACTORY_N: None,
                    self._nsb.burr_x0020_6_x0020__inten.T_TD__TAENIA_TECTA_DORSAL: None,
                    self._nsb.burr_x0020_6_x0020__inten.T_TV__TAENIA_TECTA_VENTRA: None,
                    self._nsb.burr_x0020_6_x0020__inten.DP__DORSAL_PEDUNCULAR_ARE: None,
                    self._nsb.burr_x0020_6_x0020__inten.PIR__PIRIFORM_AREA: None,
                    self._nsb.burr_x0020_6_x0020__inten.NLOT__NUCLEUS_OF_THE_LATE: None,
                    self._nsb.burr_x0020_6_x0020__inten.CO_AA__CORTICAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_6_x0020__inten.CO_AP__CORTICAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_6_x0020__inten.PAA__PIRIFORM_AMYGDALAR_A: None,
                    self._nsb.burr_x0020_6_x0020__inten.TR__POSTPIRIFORM_TRANSITI: None,
                    self._nsb.burr_x0020_6_x0020__inten.CA1__FIELD_CA1: None,
                    self._nsb.burr_x0020_6_x0020__inten.CA2__FIELD_CA2: None,
                    self._nsb.burr_x0020_6_x0020__inten.CA3__FIELD_CA3: None,
                    self._nsb.burr_x0020_6_x0020__inten.DG__DENTATE_GYRUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.FC__FASCIOLA_CINEREA: None,
                    self._nsb.burr_x0020_6_x0020__inten.IG__INDUSEUM_GRISEUM: None,
                    self._nsb.burr_x0020_6_x0020__inten.EN_TL__ENTORHINAL_AREA_LA: None,
                    self._nsb.burr_x0020_6_x0020__inten.EN_TM__ENTORHINAL_AREA_ME: None,
                    self._nsb.burr_x0020_6_x0020__inten.PAR__PARASUBICULUM: None,
                    self._nsb.burr_x0020_6_x0020__inten.POST__POSTSUBICULUM: None,
                    self._nsb.burr_x0020_6_x0020__inten.PRE__PRESUBICULUM: None,
                    self._nsb.burr_x0020_6_x0020__inten.SUB__SUBICULUM: None,
                    self._nsb.burr_x0020_6_x0020__inten.PRO_S__PROSUBICULUM: None,
                    self._nsb.burr_x0020_6_x0020__inten.HATA__HIPPOCAMPO_AMYGDALA: None,
                    self._nsb.burr_x0020_6_x0020__inten.A_PR__AREA_PROSTRIATA: None,
                    self._nsb.burr_x0020_6_x0020__inten.CLA__CLAUSTRUM: None,
                    self._nsb.burr_x0020_6_x0020__inten.E_PD__ENDOPIRIFORM_NUCLEU: None,
                    self._nsb.burr_x0020_6_x0020__inten.E_PV__ENDOPIRIFORM_NUCLEU: None,
                    self._nsb.burr_x0020_6_x0020__inten.LA__LATERAL_AMYGDALAR_NUC: None,
                    self._nsb.burr_x0020_6_x0020__inten.BLA__BASOLATERAL_AMYGDALA: None,
                    self._nsb.burr_x0020_6_x0020__inten.BMA__BASOMEDIAL_AMYGDALAR: None,
                    self._nsb.burr_x0020_6_x0020__inten.PA__POSTERIOR_AMYGDALAR_N: None,
                    self._nsb.burr_x0020_6_x0020__inten.CP__CAUDOPUTAMEN: None,
                    self._nsb.burr_x0020_6_x0020__inten.ACB__NUCLEUS_ACCUMBENS: None,
                    self._nsb.burr_x0020_6_x0020__inten.FS__FUNDUS_OF_STRIATUM: None,
                    self._nsb.burr_x0020_6_x0020__inten.OT__OLFACTORY_TUBERCLE: None,
                    self._nsb.burr_x0020_6_x0020__inten.L_SC__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.L_SR__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.L_SV__LATERAL_SEPTAL_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.SF__SEPTOFIMBRIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.SH__SEPTOHIPPOCAMPAL_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.AAA__ANTERIOR_AMYGDALAR_A: None,
                    self._nsb.burr_x0020_6_x0020__inten.BA__BED_NUCLEUS_OF_THE_AC: None,
                    self._nsb.burr_x0020_6_x0020__inten.CEA__CENTRAL_AMYGDALAR_NU: None,
                    self._nsb.burr_x0020_6_x0020__inten.IA__INTERCALATED_AMYGDALA: None,
                    self._nsb.burr_x0020_6_x0020__inten.MEA__MEDIAL_AMYGDALAR_NUC: None,
                    self._nsb.burr_x0020_6_x0020__inten.G_PE__GLOBUS_PALLIDUS_EXT: None,
                    self._nsb.burr_x0020_6_x0020__inten.G_PI__GLOBUS_PALLIDUS_INT: None,
                    self._nsb.burr_x0020_6_x0020__inten.SI__SUBSTANTIA_INNOMINATA: None,
                    self._nsb.burr_x0020_6_x0020__inten.MA__MAGNOCELLULAR_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.MS__MEDIAL_SEPTAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.NDB__DIAGONAL_BAND_NUCLEU: None,
                    self._nsb.burr_x0020_6_x0020__inten.TRS__TRIANGULAR_NUCLEUS_O: None,
                    self._nsb.burr_x0020_6_x0020__inten.BST__BED_NUCLEI_OF_THE_ST: None,
                    self._nsb.burr_x0020_6_x0020__inten.VAL__VENTRAL_ANTERIOR_LAT: None,
                    self._nsb.burr_x0020_6_x0020__inten.VM__VENTRAL_MEDIAL_NUCLEU: None,
                    self._nsb.burr_x0020_6_x0020__inten.VPL__VENTRAL_POSTEROLATER: None,
                    self._nsb.burr_x0020_6_x0020__inten.VP_LPC__VENTRAL_POSTEROLA: None,
                    self._nsb.burr_x0020_6_x0020__inten.VPM__VENTRAL_POSTEROMEDIA: None,
                    self._nsb.burr_x0020_6_x0020__inten.VP_MPC__VENTRAL_POSTEROME: None,
                    self._nsb.burr_x0020_6_x0020__inten.PO_T__POSTERIOR_TRIANGULA: None,
                    self._nsb.burr_x0020_6_x0020__inten.SPF__SUBPARAFASCICULAR_NU: None,
                    self._nsb.burr_x0020_6_x0020__inten.SPA__SUBPARAFASCICULAR_AR: None,
                    self._nsb.burr_x0020_6_x0020__inten.PP__PERIPEDUNCULAR_NUCLEU: None,
                    self._nsb.burr_x0020_6_x0020__inten.MG__MEDIAL_GENICULATE_COM: None,
                    self._nsb.burr_x0020_6_x0020__inten.L_GD__DORSAL_PART_OF_THE: None,
                    self._nsb.burr_x0020_6_x0020__inten.LP__LATERAL_POSTERIOR_NUC: None,
                    self._nsb.burr_x0020_6_x0020__inten.PO__POSTERIOR_COMPLEX_OF: None,
                    self._nsb.burr_x0020_6_x0020__inten.POL__POSTERIOR_LIMITING_N: None,
                    self._nsb.burr_x0020_6_x0020__inten.SGN__SUPRAGENICULATE_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.ETH__ETHMOID_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_6_x0020__inten.AV__ANTEROVENTRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.AM__ANTEROMEDIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.AD__ANTERODORSAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.IAM__INTERANTEROMEDIAL_NU: None,
                    self._nsb.burr_x0020_6_x0020__inten.IAD__INTERANTERODORSAL_NU: None,
                    self._nsb.burr_x0020_6_x0020__inten.LD__LATERAL_DORSAL_NUCLEU: None,
                    self._nsb.burr_x0020_6_x0020__inten.IMD__INTERMEDIODORSAL_NUC: None,
                    self._nsb.burr_x0020_6_x0020__inten.MD__MEDIODORSAL_NUCLEUS_O: None,
                    self._nsb.burr_x0020_6_x0020__inten.SMT__SUBMEDIAL_NUCLEUS_OF: None,
                    self._nsb.burr_x0020_6_x0020__inten.PR__PERIREUNENSIS_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.PVT__PARAVENTRICULAR_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.PT__PARATAENIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.RE__NUCLEUS_OF_REUNIENS: None,
                    self._nsb.burr_x0020_6_x0020__inten.XI__XIPHOID_THALAMIC_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.RH__RHOMBOID_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.CM__CENTRAL_MEDIAL_NUCLEU: None,
                    self._nsb.burr_x0020_6_x0020__inten.PCN__PARACENTRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.CL__CENTRAL_LATERAL_NUCLE: None,
                    self._nsb.burr_x0020_6_x0020__inten.PF__PARAFASCICULAR_NUCLEU: None,
                    self._nsb.burr_x0020_6_x0020__inten.PIL__POSTERIOR_INTRALAMIN: None,
                    self._nsb.burr_x0020_6_x0020__inten.RT__RETICULAR_NUCLEUS_OF: None,
                    self._nsb.burr_x0020_6_x0020__inten.IGL__INTERGENICULATE_LEAF: None,
                    self._nsb.burr_x0020_6_x0020__inten.INT_G__INTERMEDIATE_GENIC: None,
                    self._nsb.burr_x0020_6_x0020__inten.L_GV__VENTRAL_PART_OF_THE: None,
                    self._nsb.burr_x0020_6_x0020__inten.SUB_G__SUBGENICULATE_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.MH__MEDIAL_HABENULA: None,
                    self._nsb.burr_x0020_6_x0020__inten.LH__LATERAL_HABENULA: None,
                    self._nsb.burr_x0020_6_x0020__inten.SO__SUPRAOPTIC_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.PVH__PARAVENTRICULAR_HYPO: None,
                    self._nsb.burr_x0020_6_x0020__inten.P_VA__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_6_x0020__inten.P_VI__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_6_x0020__inten.ARH__ARCUATE_HYPOTHALAMIC: None,
                    self._nsb.burr_x0020_6_x0020__inten.ADP__ANTERODORSAL_PREOPTI: None,
                    self._nsb.burr_x0020_6_x0020__inten.AVP__ANTEROVENTRAL_PREOPT: None,
                    self._nsb.burr_x0020_6_x0020__inten.AVPV__ANTEROVENTRAL_PERIV: None,
                    self._nsb.burr_x0020_6_x0020__inten.DMH__DORSOMEDIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.MEPO__MEDIAN_PREOPTIC_NUC: None,
                    self._nsb.burr_x0020_6_x0020__inten.MPO__MEDIAL_PREOPTIC_AREA: None,
                    self._nsb.burr_x0020_6_x0020__inten.PS__PARASTRIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.P_VP__PERIVENTRICULAR_HYP: None,
                    self._nsb.burr_x0020_6_x0020__inten.P_VPO__PERIVENTRICULAR_HY: None,
                    self._nsb.burr_x0020_6_x0020__inten.SBPV__SUBPARAVENTRICULAR: None,
                    self._nsb.burr_x0020_6_x0020__inten.SCH__SUPRACHIASMATIC_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.SFO__SUBFORNICAL_ORGAN: None,
                    self._nsb.burr_x0020_6_x0020__inten.VMPO__VENTROMEDIAL_PREOPT: None,
                    self._nsb.burr_x0020_6_x0020__inten.VLPO__VENTROLATERAL_PREOP: None,
                    self._nsb.burr_x0020_6_x0020__inten.AHN__ANTERIOR_HYPOTHALAMI: None,
                    self._nsb.burr_x0020_6_x0020__inten.LM__LATERAL_MAMMILLARY_NU: None,
                    self._nsb.burr_x0020_6_x0020__inten.MM__MEDIAL_MAMMILLARY_NUC: None,
                    self._nsb.burr_x0020_6_x0020__inten.SUM__SUPRAMAMMILLARY_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.TM__TUBEROMAMMILLARY_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.MPN__MEDIAL_PREOPTIC_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.P_MD__DORSAL_PREMAMMILLAR: None,
                    self._nsb.burr_x0020_6_x0020__inten.P_MV__VENTRAL_PREMAMMILLA: None,
                    self._nsb.burr_x0020_6_x0020__inten.PV_HD__PARAVENTRICULAR_HY: None,
                    self._nsb.burr_x0020_6_x0020__inten.VMH__VENTROMEDIAL_HYPOTHA: None,
                    self._nsb.burr_x0020_6_x0020__inten.PH__POSTERIOR_HYPOTHALAMI: None,
                    self._nsb.burr_x0020_6_x0020__inten.LHA__LATERAL_HYPOTHALAMIC: None,
                    self._nsb.burr_x0020_6_x0020__inten.LPO__LATERAL_PREOPTIC_ARE: None,
                    self._nsb.burr_x0020_6_x0020__inten.PSTN__PARASUBTHALAMIC_NUC: None,
                    self._nsb.burr_x0020_6_x0020__inten.PE_F__PERIFORNICAL_NUCLEU: None,
                    self._nsb.burr_x0020_6_x0020__inten.RCH__RETROCHIASMATIC_AREA: None,
                    self._nsb.burr_x0020_6_x0020__inten.STN__SUBTHALAMIC_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.TU__TUBERAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.ZI__ZONA_INCERTA: None,
                    self._nsb.burr_x0020_6_x0020__inten.S_CS__SUPERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.IC__INFERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.NB__NUCLEUS_OF_THE_BRACHI: None,
                    self._nsb.burr_x0020_6_x0020__inten.SAG__NUCLEUS_SAGULUM: None,
                    self._nsb.burr_x0020_6_x0020__inten.PBG__PARABIGEMINAL_NUCLEU: None,
                    self._nsb.burr_x0020_6_x0020__inten.S_NR__SUBSTANTIA_NIGRA_RE: None,
                    self._nsb.burr_x0020_6_x0020__inten.VTA__VENTRAL_TEGMENTAL_AR: None,
                    self._nsb.burr_x0020_6_x0020__inten.PN__PARANIGRAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.RR__MIDBRAIN_RETICULAR_NU: None,
                    self._nsb.burr_x0020_6_x0020__inten.MRN__MIDBRAIN_RETICULAR_N: None,
                    self._nsb.burr_x0020_6_x0020__inten.S_CM__SUPERIOR_COLLICULUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.PAG__PERIAQUEDUCTAL_GRAY: None,
                    self._nsb.burr_x0020_6_x0020__inten.APN__ANTERIOR_PRETECTAL_N: None,
                    self._nsb.burr_x0020_6_x0020__inten.MPT__MEDIAL_PRETECTAL_ARE: None,
                    self._nsb.burr_x0020_6_x0020__inten.NOT__NUCLEUS_OF_THE_OPTIC: None,
                    self._nsb.burr_x0020_6_x0020__inten.NPC__NUCLEUS_OF_THE_POSTE: None,
                    self._nsb.burr_x0020_6_x0020__inten.OP__OLIVARY_PRETECTAL_NUC: None,
                    self._nsb.burr_x0020_6_x0020__inten.PPT__POSTERIOR_PRETECTAL: None,
                    self._nsb.burr_x0020_6_x0020__inten.RPF__RETROPARAFASCICULAR: None,
                    self._nsb.burr_x0020_6_x0020__inten.CUN__CUNEIFORM_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.RN__RED_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.III__OCULOMOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.MA3__MEDIAL_ACCESORY_OCUL: None,
                    self._nsb.burr_x0020_6_x0020__inten.EW__EDINGER__WESTPHAL_NUC: None,
                    self._nsb.burr_x0020_6_x0020__inten.IV__TROCHLEAR_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.PA4__PARATROCHLEAR_NUCLEU: None,
                    self._nsb.burr_x0020_6_x0020__inten.VTN__VENTRAL_TEGMENTAL_NU: None,
                    self._nsb.burr_x0020_6_x0020__inten.AT__ANTERIOR_TEGMENTAL_NU: None,
                    self._nsb.burr_x0020_6_x0020__inten.LT__LATERAL_TERMINAL_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.DT__DORSAL_TERMINAL_NUCLE: None,
                    self._nsb.burr_x0020_6_x0020__inten.MT__MEDIAL_TERMINAL_NUCLE: None,
                    self._nsb.burr_x0020_6_x0020__inten.S_NC__SUBSTANTIA_NIGRA_CO: None,
                    self._nsb.burr_x0020_6_x0020__inten.PPN__PEDUNCULOPONTINE_NUC: None,
                    self._nsb.burr_x0020_6_x0020__inten.IF__INTERFASCICULAR_NUCLE: None,
                    self._nsb.burr_x0020_6_x0020__inten.IPN__INTERPEDUNCULAR_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.RL__ROSTRAL_LINEAR_NUCLEU: None,
                    self._nsb.burr_x0020_6_x0020__inten.CLI__CENTRAL_LINEAR_NUCLE: None,
                    self._nsb.burr_x0020_6_x0020__inten.DR__DORSAL_NUCLEUS_RAPHE: None,
                    self._nsb.burr_x0020_6_x0020__inten.NLL__NUCLEUS_OF_THE_LATER: None,
                    self._nsb.burr_x0020_6_x0020__inten.PSV__PRINCIPAL_SENSORY_NU: None,
                    self._nsb.burr_x0020_6_x0020__inten.PB__PARABRACHIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.SOC__SUPERIOR_OLIVARY_COM: None,
                    self._nsb.burr_x0020_6_x0020__inten.B__BARRINGTON_S_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.DTN__DORSAL_TEGMENTAL_NUC: None,
                    self._nsb.burr_x0020_6_x0020__inten.PD_TG__POSTERODORSAL_TEGM: None,
                    self._nsb.burr_x0020_6_x0020__inten.PCG__PONTINE_CENTRAL_GRAY: None,
                    self._nsb.burr_x0020_6_x0020__inten.PG__PONTINE_GRAY: None,
                    self._nsb.burr_x0020_6_x0020__inten.PR_NC__PONTINE_RETICULAR: None,
                    self._nsb.burr_x0020_6_x0020__inten.SG__SUPRAGENUAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.SUT__SUPRATRIGEMINAL_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.TRN__TEGMENTAL_RETICULAR: None,
                    self._nsb.burr_x0020_6_x0020__inten.V__MOTOR_NUCLEUS_OF_TRIGE: None,
                    self._nsb.burr_x0020_6_x0020__inten.P5__PERITRIGEMINAL_ZONE: None,
                    self._nsb.burr_x0020_6_x0020__inten.ACS5__ACCESSORY_TRIGEMINA: None,
                    self._nsb.burr_x0020_6_x0020__inten.PC5__PARVICELLULAR_MOTOR: None,
                    self._nsb.burr_x0020_6_x0020__inten.I5__INTERTRIGEMINAL_NUCLE: None,
                    self._nsb.burr_x0020_6_x0020__inten.CS__SUPERIOR_CENTRAL_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.LC__LOCUS_CERULEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.LDT__LATERODORSAL_TEGMENT: None,
                    self._nsb.burr_x0020_6_x0020__inten.NI__NUCLEUS_INCERTUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.PR_NR__PONTINE_RETICULAR: None,
                    self._nsb.burr_x0020_6_x0020__inten.RPO__NUCLEUS_RAPHE_PONTIS: None,
                    self._nsb.burr_x0020_6_x0020__inten.SLC__SUBCERULEUS_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.SLD__SUBLATERODORSAL_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.MY__MEDULLA: None,
                    self._nsb.burr_x0020_6_x0020__inten.AP__AREA_POSTREMA: None,
                    self._nsb.burr_x0020_6_x0020__inten.DCO__DORSAL_COCHLEAR_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.VCO__VENTRAL_COCHLEAR_NUC: None,
                    self._nsb.burr_x0020_6_x0020__inten.CU__CUNEATE_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.GR__GRACILE_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.ECU__EXTERNAL_CUNEATE_NUC: None,
                    self._nsb.burr_x0020_6_x0020__inten.NTB__NUCLEUS_OF_THE_TRAPE: None,
                    self._nsb.burr_x0020_6_x0020__inten.NTS__NUCLEUS_OF_THE_SOLIT: None,
                    self._nsb.burr_x0020_6_x0020__inten.SPVC__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_6_x0020__inten.SPVI__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_6_x0020__inten.SPVO__SPINAL_NUCLEUS_OF_T: None,
                    self._nsb.burr_x0020_6_x0020__inten.PA5__PARATRIGEMINAL_NUCLE: None,
                    self._nsb.burr_x0020_6_x0020__inten.VI__ABDUCENS_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.VII__FACIAL_MOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.AMB__NUCLEUS_AMBIGUUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.DMX__DORSAL_MOTOR_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.GRN__GIGANTOCELLULAR_RETI: None,
                    self._nsb.burr_x0020_6_x0020__inten.ICB__INFRACEREBELLAR_NUCL: None,
                    self._nsb.burr_x0020_6_x0020__inten.IO__INFERIOR_OLIVARY_COMP: None,
                    self._nsb.burr_x0020_6_x0020__inten.IRN__INTERMEDIATE_RETICUL: None,
                    self._nsb.burr_x0020_6_x0020__inten.ISN__INFERIOR_SALIVATORY: None,
                    self._nsb.burr_x0020_6_x0020__inten.LIN__LINEAR_NUCLEUS_OF_TH: None,
                    self._nsb.burr_x0020_6_x0020__inten.LRN__LATERAL_RETICULAR_NU: None,
                    self._nsb.burr_x0020_6_x0020__inten.MARN__MAGNOCELLULAR_RETIC: None,
                    self._nsb.burr_x0020_6_x0020__inten.MDRN__MEDULLARY_RETICULAR: None,
                    self._nsb.burr_x0020_6_x0020__inten.PARN__PARVICELLULAR_RETIC: None,
                    self._nsb.burr_x0020_6_x0020__inten.PAS__PARASOLITARY_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.PGRN__PARAGIGANTOCELLULAR: None,
                    self._nsb.burr_x0020_6_x0020__inten.NR__NUCLEUS_OF__ROLLER: None,
                    self._nsb.burr_x0020_6_x0020__inten.PRP__NUCLEUS_PREPOSITUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.PMR__PARAMEDIAN_RETICULAR: None,
                    self._nsb.burr_x0020_6_x0020__inten.PPY__PARAPYRAMIDAL_NUCLEU: None,
                    self._nsb.burr_x0020_6_x0020__inten.LAV__LATERAL_VESTIBULAR_N: None,
                    self._nsb.burr_x0020_6_x0020__inten.MV__MEDIAL_VESTIBULAR_NUC: None,
                    self._nsb.burr_x0020_6_x0020__inten.SPIV__SPINAL_VESTIBULAR_N: None,
                    self._nsb.burr_x0020_6_x0020__inten.SUV__SUPERIOR_VESTIBULAR: None,
                    self._nsb.burr_x0020_6_x0020__inten.X__NUCLEUS_X: None,
                    self._nsb.burr_x0020_6_x0020__inten.XII__HYPOGLOSSAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.Y__NUCLEUS_Y: None,
                    self._nsb.burr_x0020_6_x0020__inten.RM__NUCLEUS_RAPHE_MAGNUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.RPA__NUCLEUS_RAPHE_PALLID: None,
                    self._nsb.burr_x0020_6_x0020__inten.RO__NUCLEUS_RAPHE_OBSCURU: None,
                    self._nsb.burr_x0020_6_x0020__inten.LING__LINGULA_I: None,
                    self._nsb.burr_x0020_6_x0020__inten.CENT2__LOBULE_II: None,
                    self._nsb.burr_x0020_6_x0020__inten.CENT3__LOBULE_III: None,
                    self._nsb.burr_x0020_6_x0020__inten.CUL4_5__LOBULES_IV_V: None,
                    self._nsb.burr_x0020_6_x0020__inten.DEC__DECLIVE_VI: None,
                    self._nsb.burr_x0020_6_x0020__inten.FOTU__FOLIUM_TUBER_VERMIS: None,
                    self._nsb.burr_x0020_6_x0020__inten.PYR__PYRAMUS_VIII: None,
                    self._nsb.burr_x0020_6_x0020__inten.UVU__UVULA_IX: None,
                    self._nsb.burr_x0020_6_x0020__inten.NOD__NODULUS_X: None,
                    self._nsb.burr_x0020_6_x0020__inten.SIM__SIMPLE_LOBULE: None,
                    self._nsb.burr_x0020_6_x0020__inten.A_NCR1__CRUS_1: None,
                    self._nsb.burr_x0020_6_x0020__inten.A_NCR2__CRUS_2: None,
                    self._nsb.burr_x0020_6_x0020__inten.PRM__PARAMEDIAN_LOBULE: None,
                    self._nsb.burr_x0020_6_x0020__inten.COPY__COPULA_PYRAMIDIS: None,
                    self._nsb.burr_x0020_6_x0020__inten.PFL__PARAFLOCCULUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.FL__FLOCCULUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.FN__FASTIGIAL_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.IP__INTERPOSED_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.DN__DENTATE_NUCLEUS: None,
                    self._nsb.burr_x0020_6_x0020__inten.VE_CB__VESTIBULOCEREBELLA: None,
                }.get(self._nsb.burr_x0020_6_x0020__inten, None)
            )
    
        @property
        def aind_burr_x0020_6_x0020_a_x002(self) -> Optional[str]:
            """Maps burr_x0020_6_x0020_a_x002 to aind model."""
            return self._nsb.burr_x0020_6_x0020_a_x002

    @property
        def aind_burr_x0020_4_x0020__injec_002(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__injec_002 to aind model."""
            return self._nsb.burr_x0020_4_x0020__injec_002

    @property
        def aind_burr_x0020_4_x0020__injec_007(self) -> Optional[str]:
            """Maps burr_x0020_4_x0020__injec_007 to aind model."""
            return self._nsb.burr_x0020_4_x0020__injec_007

    @property
        def aind_burr_x0020_5_x0020_intend_002(self) -> Optional[Any]:
            """Maps burr_x0020_5_x0020_intend_002 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_5_x0020_intend_002 is None
                else {
                    self._nsb.burr_x0020_5_x0020_intend_002.N_A: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.DOPAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.SEROTONIN: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.HISTAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.GLUTAMATE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.GABA: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.CALCIUM: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.VOLTAGE: None,
                    self._nsb.burr_x0020_5_x0020_intend_002.CONTROL: None,
                }.get(self._nsb.burr_x0020_5_x0020_intend_002, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020_intend_003(self) -> Optional[Any]:
            """Maps burr_x0020_5_x0020_intend_003 to aind model."""
            return (
                None
                if self._nsb.burr_x0020_5_x0020_intend_003 is None
                else {
                    self._nsb.burr_x0020_5_x0020_intend_003.N_A: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.DOPAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.SEROTONIN: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.NOREPINEPHRINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.ACETYLCHOLINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.HISTAMINE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.GLUTAMATE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.GABA: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.CALCIUM: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.VOLTAGE: None,
                    self._nsb.burr_x0020_5_x0020_intend_003.CONTROL: None,
                }.get(self._nsb.burr_x0020_5_x0020_intend_003, None)
            )
    
        @property
        def aind_burr_x0020_5_x0020_m_x002(self) -> Optional[str]:
            """Maps burr_x0020_5_x0020_m_x002 to aind model."""
            return self._nsb.burr_x0020_5_x0020_m_x002

    @property
        def aind_care_x0020__moduele(self) -> Optional[Any]:
            """Maps care_x0020__moduele to aind model."""
            return (
                None
                if self._nsb.care_x0020__moduele is None
                else {
                    self._nsb.care_x0020__moduele.SELECT: None,
                    self._nsb.care_x0020__moduele.CM_S_01_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_01_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_03_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_03_C_D: None,
                    self._nsb.care_x0020__moduele.CM_S_04_A_B: None,
                    self._nsb.care_x0020__moduele.CM_S_04_C_D: None,
                }.get(self._nsb.care_x0020__moduele, None)
            )
    
        @property
        def aind_color_tag(self) -> Optional[str]:
            """Maps color_tag to aind model."""
            return self._nsb.color_tag

    @property
        def aind_burr5_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr5_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr5_x0020__perform_x002 is None
                else {
                    self._nsb.burr5_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr5_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr5_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr5_x0020__status(self) -> Optional[Any]:
            """Maps burr5_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr5_x0020__status is None
                else {
                    self._nsb.burr5_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr5_x0020__status, None)
            )
    
        @property
        def aind_burr5_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr5_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr5_x0020__virus_x0020 is None
                else {
                    self._nsb.burr5_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr5_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr5_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr6_x0020__injection_x0(self) -> Optional[Any]:
            """Maps burr6_x0020__injection_x0 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__injection_x0 is None
                else {
                    self._nsb.burr6_x0020__injection_x0.SELECT: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_1: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_1: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_2: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_2: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_3: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_3: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_4: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_4: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_5: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_5: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_6: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_6: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_7: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_7: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_8: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_8: None,
                    self._nsb.burr6_x0020__injection_x0.NANO_9: None,
                    self._nsb.burr6_x0020__injection_x0.IONTO_9: None,
                }.get(self._nsb.burr6_x0020__injection_x0, None)
            )
    
        @property
        def aind_burr6_x0020__perform_x002(self) -> Optional[Any]:
            """Maps burr6_x0020__perform_x002 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__perform_x002 is None
                else {
                    self._nsb.burr6_x0020__perform_x002.INITIAL__SURGERY: None,
                    self._nsb.burr6_x0020__perform_x002.FOLLOW_UP__SURGERY: None,
                }.get(self._nsb.burr6_x0020__perform_x002, None)
            )
    
        @property
        def aind_burr6_x0020__status(self) -> Optional[Any]:
            """Maps burr6_x0020__status to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__status is None
                else {
                    self._nsb.burr6_x0020__status.COMPLETE: None,
                }.get(self._nsb.burr6_x0020__status, None)
            )
    
        @property
        def aind_burr6_x0020__virus_x0020(self) -> Optional[Any]:
            """Maps burr6_x0020__virus_x0020 to aind model."""
            return (
                None
                if self._nsb.burr6_x0020__virus_x0020 is None
                else {
                    self._nsb.burr6_x0020__virus_x0020.SELECT: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1_AAV__BEADS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_1__OTHER__WRITE_IN_CO: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__RABIES: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_CAV: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_6_OHDA: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__SINDBIS: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2_HSV_1: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__LENTI: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__CHOLERA__TOXIN_B: None,
                    self._nsb.burr6_x0020__virus_x0020.BSL_2__OTHER__WRITE_IN_CO: None,
                }.get(self._nsb.burr6_x0020__virus_x0020, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__fiber(self) -> Optional[Any]:
            """Maps burr_x0020_1_x0020__fiber to aind model."""
            return (
                None
                if self._nsb.burr_x0020_1_x0020__fiber is None
                else {
                    self._nsb.burr_x0020_1_x0020__fiber.STANDARD_PROVIDED_BY_NSB: None,
                    self._nsb.burr_x0020_1_x0020__fiber.CUSTOM: None,
                }.get(self._nsb.burr_x0020_1_x0020__fiber, None)
            )
    
        @property
        def aind_burr_x0020_1_x0020__grid(self) -> Optional[str]:
            """Maps burr_x0020_1_x0020__grid to aind model."""
            return self._nsb.burr_x0020_1_x0020__grid

    @property
        def aind_procedure_x0020__slots(self) -> Optional[Any]:
            """Maps procedure_x0020__slots to aind model."""
            return (
                None
                if self._nsb.procedure_x0020__slots is None
                else {
                    self._nsb.procedure_x0020__slots.SELECT: None,
                    self._nsb.procedure_x0020__slots.SINGLE_SURGICAL_SESSION: None,
                    self._nsb.procedure_x0020__slots.INITIAL_SURGERY_WITH_FOLL: None,
                }.get(self._nsb.procedure_x0020__slots, None)
            )
    
        @property
        def aind_procedure_x0020_t2(self) -> Optional[Any]:
            """Maps procedure_x0020_t2 to aind model."""
            return (
                None
                if self._nsb.procedure_x0020_t2 is None
                else {
                    self._nsb.procedure_x0020_t2.SELECT: None,
                    self._nsb.procedure_x0020_t2.N_2_P: None,
                    self._nsb.procedure_x0020_t2.NP: None,
                    self._nsb.procedure_x0020_t2.N_A: None,
                }.get(self._nsb.procedure_x0020_t2, None)
            )
    
        @property
        def aind_project_id(self) -> Optional[Any]:
            """Maps project_id to aind model."""
            return (
                None
                if self._nsb.project_id is None
                else {
                    self._nsb.project_id.N_101_03_001_10__COSTA_PG: None,
                    self._nsb.project_id.N_102_01_009_10_CTY__MORP: None,
                    self._nsb.project_id.N_102_01_011_10_CTY__CONN: None,
                    self._nsb.project_id.N_102_01_012_10_CTY__CONN: None,
                    self._nsb.project_id.N_102_01_016_10_CTY__TAXO: None,
                    self._nsb.project_id.N_102_01_029_20_CTY_BRAIN: None,
                    self._nsb.project_id.N_102_01_031_20_W4_CTY_EU: None,
                    self._nsb.project_id.N_102_01_031_20_W5_CTY_EU: None,
                    self._nsb.project_id.N_102_01_032_20_CTY__MOUS: None,
                    self._nsb.project_id.N_102_01_036_20_CTY__DISS: None,
                    self._nsb.project_id.N_102_01_040_20_CTY_BRAIN: None,
                    self._nsb.project_id.N_102_01_043_20_CTY__OPTI: None,
                    self._nsb.project_id.N_102_01_044_10_CTY__GENO: None,
                    self._nsb.project_id.N_102_01_045_10_CTY_IVSCC: None,
                    self._nsb.project_id.N_102_01_046_20_CTY__WEIL: None,
                    self._nsb.project_id.N_102_01_048_10_CTY__BARC: None,
                    self._nsb.project_id.N_102_01_049_20_CTY__OPIO: None,
                    self._nsb.project_id.N_102_01_054_20_CTY_PFAC: None,
                    self._nsb.project_id.N_102_01_055_20_CTY_EM__M: None,
                    self._nsb.project_id.N_102_01_059_20_CTY_SCORC: None,
                    self._nsb.project_id.N_102_01_060_20_CTY__BRAI: None,
                    self._nsb.project_id.N_102_01_061_20_CTY_BICAN: None,
                    self._nsb.project_id.N_102_01_062_20_CTY_BICAN: None,
                    self._nsb.project_id.N_102_01_064_10_CTY__GENE: None,
                    self._nsb.project_id.N_102_01_066_20_AIBS_CTY: None,
                    self._nsb.project_id.N_102_01_066_20_AIND_CTY: None,
                    self._nsb.project_id.N_102_01_068_20_CTY_CONNE: None,
                    self._nsb.project_id.N_102_01_069_20__PRE__SPE: None,
                    self._nsb.project_id.N_102_01_070_20_CTY_CONNE: None,
                    self._nsb.project_id.N_102_01_078_20_AIBS__VOC: None,
                    self._nsb.project_id.N_102_01_079_20_AIBS_CONN: None,
                    self._nsb.project_id.N_102_01_999_10_CTY__PROG: None,
                    self._nsb.project_id.N_102_02_004_10_BTV__VISU: None,
                    self._nsb.project_id.N_102_02_012_20_BTV_BRAIN: None,
                    self._nsb.project_id.N_102_04_004_10_OTH__MERI: None,
                    self._nsb.project_id.N_102_04_006_20_OTH__MEAS: None,
                    self._nsb.project_id.N_102_04_007_10_APLD__TAR: None,
                    self._nsb.project_id.N_102_04_010_10_CTY_SR_SL: None,
                    self._nsb.project_id.N_102_04_011_10_CTY_SR_SY: None,
                    self._nsb.project_id.N_102_04_012_10_CTY_SR__F: None,
                    self._nsb.project_id.N_102_04_014_10_CTY__PARK: None,
                    self._nsb.project_id.N_102_04_016_20_CTY__DRAV: None,
                    self._nsb.project_id.N_102_88_001_10_XPG__CORE: None,
                    self._nsb.project_id.N_102_88_003_10__ANIMAL: None,
                    self._nsb.project_id.N_102_88_005_10__TRANSGEN: None,
                    self._nsb.project_id.N_102_88_008_10__LAB__ANI: None,
                    self._nsb.project_id.N_106_01_001_10__IMMUNOLO: None,
                    self._nsb.project_id.N_110_01_001_10_PG__PROTE: None,
                    self._nsb.project_id.N_121_01_016_20_MSP_BRAIN: None,
                    self._nsb.project_id.N_121_01_018_20_MSP__EPHA: None,
                    self._nsb.project_id.N_121_01_023_20_MSP__TEMP: None,
                    self._nsb.project_id.N_121_01_025_20_MSP_U01: None,
                    self._nsb.project_id.N_121_01_026_20_MSP__TEMP: None,
                    self._nsb.project_id.N_122_01_001_10_AIND__SCI: None,
                    self._nsb.project_id.N_122_01_002_20__MOLECULA: None,
                    self._nsb.project_id.N_122_01_002_20__PROJECT: None,
                    self._nsb.project_id.N_122_01_002_20__PROJECT_2: None,
                    self._nsb.project_id.N_122_01_002_20__PROJECT_3: None,
                    self._nsb.project_id.N_122_01_004_20_AIND__BRA: None,
                    self._nsb.project_id.N_122_01_010_20_AIND__POO: None,
                    self._nsb.project_id.N_122_01_011_20_AIND__COH: None,
                    self._nsb.project_id.N_122_01_012_20_AIND_RF1: None,
                    self._nsb.project_id.N_122_01_013_10_MSP__SCIE: None,
                    self._nsb.project_id.N_122_01_014_20_AIND__SIE: None,
                    self._nsb.project_id.N_122_01_019_20_AIND_CZI: None,
                    self._nsb.project_id.N_122_01_020_20_AIBS__COH: None,
                    self._nsb.project_id.N_122_01_020_20_AIND__COH: None,
                    self._nsb.project_id.N_122_01_022_20_AIND__POD: None,
                    self._nsb.project_id.N_123_01_003_20__MOTOR__C: None,
                    self._nsb.project_id.N_124_01_001_10__BRAIN__C: None,
                    self._nsb.project_id.N_125_01_001_10__SEA_HUB: None,
                    self._nsb.project_id.AAV_PRODUCTION_102_88_004: None,
                    self._nsb.project_id.R_D_102_88_004_10: None,
                }.get(self._nsb.project_id, None)
            )
    
        @property
        def aind_protocol(self) -> Optional[Any]:
            """Maps protocol to aind model."""
            return (
                None
                if self._nsb.protocol is None
                else {
                    self._nsb.protocol.SELECT: None,
                    self._nsb.protocol.N_2119__TRAINING_AND_QUAL: None,
                    self._nsb.protocol.N_2201__INTERROGATING_PRO: None,
                    self._nsb.protocol.N_2202__TESTING_AA_VS_IN: None,
                    self._nsb.protocol.N_2204__PRIMARY_NEURON_AN: None,
                    self._nsb.protocol.N_2205__OPTIMIZATION_AND: None,
                    self._nsb.protocol.N_2207__IN__VITRO__BRAIN: None,
                    self._nsb.protocol.N_2212__INVESTIGATING__BR: None,
                    self._nsb.protocol.N_2301__TESTING_OF_ENHANC: None,
                    self._nsb.protocol.N_2304__NEUROSURGERY__BEH: None,
                    self._nsb.protocol.N_2305__IN__VIVO__BRAIN: None,
                    self._nsb.protocol.N_2306__PATCH_SEQ_CHARACT: None,
                    self._nsb.protocol.N_2307__DISSECTING_THE_NE: None,
                    self._nsb.protocol.N_2308__INDUCTION_OF__IMM: None,
                    self._nsb.protocol.N_2401__THE_USE_OF_MICE_F: None,
                    self._nsb.protocol.N_2402__BRAIN__OBSERVATOR: None,
                    self._nsb.protocol.N_2403__ELECTROPHYSIOLOGY: None,
                    self._nsb.protocol.N_2405__ANALYSIS_OF__INTE: None,
                    self._nsb.protocol.N_2406__CHARACTERIZATION: None,
                    self._nsb.protocol.N_2410__VALIDATION_OF_BRA: None,
                    self._nsb.protocol.N_2412__CIRCUIT_TRACING_A: None,
                    self._nsb.protocol.N_2413__NEUROPHYSIOLOGY_O: None,
                    self._nsb.protocol.N_2414__ELECTROPHYSIOLOGI: None,
                    self._nsb.protocol.N_2415__OPTOPHYSIOLOGICAL: None,
                    self._nsb.protocol.N_2416__ANATOMICAL_ANALYS: None,
                    self._nsb.protocol.N_2417__CHARACTERIZATION: None,
                    self._nsb.protocol.N_2418__IN__VITRO__SINGLE: None,
                    self._nsb.protocol.N_2427__OPEN_SCOPE__MINDS: None,
                }.get(self._nsb.protocol, None)
            )
    
        @property
        def aind_ret_setting0(self) -> Optional[Any]:
            """Maps ret_setting0 to aind model."""
            return (
                None
                if self._nsb.ret_setting0 is None
                else {
                    self._nsb.ret_setting0.OFF: None,
                    self._nsb.ret_setting0.ON: None,
                }.get(self._nsb.ret_setting0, None)
            )
    
        @property
        def aind_ret_setting1(self) -> Optional[Any]:
            """Maps ret_setting1 to aind model."""
            return (
                None
                if self._nsb.ret_setting1 is None
                else {
                    self._nsb.ret_setting1.OFF: None,
                    self._nsb.ret_setting1.ON: None,
                }.get(self._nsb.ret_setting1, None)
            )
    
        @property
        def aind_round1_inj_isolevel(self) -> Optional[str]:
            """Maps round1_inj_isolevel to aind model."""
            return self._nsb.round1_inj_isolevel

    @property
        def aind_edit(self) -> Optional[str]:
            """Maps edit to aind model."""
            return self._nsb.edit
