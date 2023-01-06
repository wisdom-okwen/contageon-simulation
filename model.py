"""The model classes maintain the state and logic of the simulation."""

from __future__ import annotations
from random import random
from exercises.ex09 import constants
from math import sin, cos, pi, sqrt


__author__ = "730574299"  


class Point:
    """A model of a 2-d cartesian coordinate Point."""
    x: float
    y: float

    def __init__(self, x: float, y: float):
        """Construct a point with x, y coordinates."""
        self.x = x
        self.y = y

    def add(self, other: Point) -> Point:
        """Add two Point objects together and return a new Point."""
        x: float = self.x + other.x
        y: float = self.y + other.y
        return Point(x, y)
    
    def distance(self, other: Point) -> float:
        """Distance between the centers of two cells."""
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class Cell:
    """An individual subject in the simulation."""
    location: Point
    direction: Point
    sickness: int = constants.VULNERABLE

    def __init__(self, location: Point, direction: Point):
        """Construct a cell with its location and direction."""
        self.location = location
        self.direction = direction

    def tick(self) -> None:
        """Tick of the cell."""
        self.location = self.location.add(self.direction)  
        if self.is_infected():
            self.sickness += 1
            
        if self.sickness > constants.RECOVERY_PERIOD:
            self.immunize()      
         
    def color(self) -> str:
        """Return the color representation of a cell."""
        red: str = constants.RED
        green: str = constants.GREEN
        gray: str = constants.GRAY
        if self.is_infected():
            return red   
        elif self.is_vulnerable():
            return gray
        elif self.is_immune():
            return green
    
    def contract_disease(self) -> None:
        """Assign infection to sickness."""
        self.sickness = constants.INFECTED       
        
    def is_vulnerable(self) -> bool:
        """Check if cell is vulnerable."""
        return self.sickness == constants.VULNERABLE
        
    def is_infected(self) -> bool:
        """Check if cell is infected."""
        return self.sickness >= constants.INFECTED

    def contact_with(self, other: Cell) -> None:
        """Contract disease when vulnerable cell meets infected cell."""
        if self.is_infected() and other.is_vulnerable():
            other.contract_disease()
        elif other.is_infected() and self.is_vulnerable():
            self.contract_disease()
               
    def immunize(self) -> None:
        """Make cell immune."""
        self.sickness = constants.IMMUNE
               
    def is_immune(self) -> None:
        """Check if a cell is immune."""
        return self.sickness == constants.IMMUNE


class Model:
    """The state of the simulation."""

    population: list[Cell]
    time: int = 0

    def __init__(self, cells: int, speed: float, initial_infections: int, immune: int = 0):
        """Initialize the cells with random locations and directions."""
        if initial_infections <= 0:
            raise ValueError("Some cells must be initially infected.")
        elif initial_infections >= cells:
            raise ValueError("Number of infected cells must be less than total number of cells.")
        if immune >= cells:
            raise ValueError("Number of immune cells must be less than total number of cells.")
        elif immune < 0:
            raise ValueError("Number of immune cells must be zero or more.")
        
        self.population: list[Cell] = []
        for i in range(cells):
            start_direction: Point = self.random_direction(speed)
            start_location: Point = self.random_location()
            cell: Cell = Cell(start_location, start_direction)
            if i < initial_infections:
                cell.contract_disease()
            if i < immune:
                cell.immunize()
            self.population.append(cell)
            
    def tick(self) -> None:
        """Update the state of the simulation by one time step."""
        self.time += 1
        for cell in self.population:
            cell.tick()
            self.enforce_bounds(cell)
        self.check_contacts()

    def random_location(self) -> Point:
        """Generate a random location."""
        start_x: float = random() * constants.BOUNDS_WIDTH - constants.MAX_X
        start_y: float = random() * constants.BOUNDS_HEIGHT - constants.MAX_Y
        return Point(start_x, start_y)

    def random_direction(self, speed: float) -> Point:
        """Generate a 'point' used as a directional vector."""
        random_angle: float = 2.0 * pi * random()
        direction_x: float = cos(random_angle) * speed
        direction_y: float = sin(random_angle) * speed
        return Point(direction_x, direction_y)

    def enforce_bounds(self, cell: Cell) -> None:
        """Cause a cell to 'bounce' if it goes out of bounds."""
        if cell.location.x > constants.MAX_X or cell.location.x < constants.MIN_X:
            cell.direction.x *= -1.0
        if cell.location.y > constants.MAX_Y or cell.location.y < constants.MIN_Y:
            cell.direction.y *= -1.0
    
    def is_complete(self) -> bool:
        """Method to indicate when the simulation is complete."""
        for cell in self.population:
            if cell.is_infected():
                return False
        return True
     
    def check_contacts(self) -> None:
        """Check for contact between two cells."""
        for i in range(len(self.population)):
            for j in range(i + 1, len(self.population)):
                cell1: Cell = self.population[i]
                cell2: Cell = self.population[j]
                if cell1.location.distance(cell2.location) < constants.CELL_RADIUS:
                    cell1.contact_with(cell2)