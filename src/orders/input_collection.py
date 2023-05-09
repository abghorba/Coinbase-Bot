class InputCollector:
    def __init__(self):
        self.start_date = None
        self.start_time = None
        self.frequency = None
        self.orders = None

    def get_start_date(self):
        """Checks if the start date the user inputs is valid."""

        return NotImplementedError()

    def get_start_time(self):
        """Checks if the start time the user inputs is valid."""

        return NotImplementedError()

    def get_start_datetime(self):
        """Checks if the start date and time the user inputs is valid."""

        return NotImplementedError()

    def get_frequency(self):
        """Checks if the frequency the user inputs is valid."""

        return NotImplementedError()

    def get_orders(self):
        """Constructs a dictionary of valid orders."""

        return NotImplementedError()

    def collect_inputs(self):
        """Driver function to collect user inputs."""

        return NotImplementedError()
