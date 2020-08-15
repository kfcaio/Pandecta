from __future__ import annotations
import datetime
from abc import ABC, abstractmethod
from typing import Iterator, List

import regex
import click


class RobotHandler:
    
    def __init__(self, robot: GenericRobot) -> None:
        self._robot = robot

    @property
    def robot(self) -> GenericRobot:
        return self._robot

    @robot.setter
    def robot(self, robot: GenericRobot) -> None:
        self._robot = robot
    
    @staticmethod
    def get_publications(
        date: datetime.datetime, 
        force: bool
    ) -> Iterator[dict]:
        yield '/home/kfcaio/pandecta/sample.pdf'
    
    def collect(
        self, 
        date: datetime.datetime, 
        force: bool = False, 
        prod: bool = False
    ) -> Iterator[dict]:
        publications = self.get_publications(date, force)
        results = self._robot.search(publications)

        final = []

        last_hierarchy = []
        current_hierarchy = []
        snippet = ''

        for el, page in results:
            if el['hierarchy']:
                match = regex.search(self.robot.BLOCK_PATTERN, snippet)

                if match:
                    aqui = {
                        'text': snippet,
                        'sections': [current_hierarchy, last_hierarchy]
                    }
                    final.append(aqui)

                snippet = ''
                current_hierarchy = el['hierarchy']

            else:
                snippet += el['text']
            
            if last_hierarchy:
                if last_hierarchy != current_hierarchy:
                    last_hierarchy = current_hierarchy

        return final

class GenericRobot(ABC):

    @abstractmethod
    def search(
        self, 
        publications: List[dict]
    ) -> Iterator[dict]:
        pass

def setup(robot):
    global _robot
    _robot = robot

    cli()

@click.command()
@click.option(
    '-d', 
    '--date', 
    default=datetime.datetime.now().strftime(r'%Y-%m-%d'),
    type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('-f', '--force', default=False, is_flag=True)
@click.option('-p', '--prod', default=False, is_flag=True)
def cli(date, force, prod):
    global _robot

    handler = RobotHandler(_robot())
    results = handler.collect(date=date, force=force, prod=prod)

    import pdb
    pdb.set_trace()

    return
