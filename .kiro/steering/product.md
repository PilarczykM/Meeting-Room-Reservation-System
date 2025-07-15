# Meeting Room Reservation System

## Product Overview
A simple CLI application for managing bookings for a single conference room. Users can reserve time slots, cancel existing bookings, and view all reservations.

## Core Features
- **Book a Room**: Reserve time slots with attendee count (4-20 people)
- **Cancel Booking**: Remove reservations using unique booking ID
- **View Reservations**: List all current bookings

## Business Rules
- No overlapping bookings allowed
- Attendee count must be between 4-20 (inclusive)
- Room capacity is 20 people maximum
- Each booking gets a unique identifier

## Domain Model
- **Meeting Room**: Aggregate root managing all bookings and enforcing business rules
- **Booking**: Individual reservation with time slot, booker details, and attendee count
- **Time Slot**: Represents booking duration with start/end times

## Key Constraints
- Single conference room only
- No user authentication required
- All operations must maintain booking integrity
- Time slots cannot overlap with existing reservations