class IObserver:
    def update(self, mensaje): pass

class LoggerObserver(IObserver):
    def update(self, mensaje):
        print(f"[LOG DEL SISTEMA]: {mensaje}")

class Subject:
    def __init__(self):
        self._observers = []
    def attach(self, observer):
        self._observers.append(observer)
    def notify(self, mensaje):
        for observer in self._observers:
            observer.update(mensaje)