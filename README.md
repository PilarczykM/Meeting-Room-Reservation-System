# Meeting Room Reservation System

## Overview
The Meeting Room Reservation System is a simple application designed to manage bookings for a single conference room. Users can reserve the room for specific time slots, cancel existing bookings, and view all reservations. The system ensures that no overlapping bookings occur and enforces constraints on the number of attendees per booking, maintaining the integrity of the reservation schedule.

## Features
- **Book a Room**: Users can reserve the conference room by specifying a start time, end time, their details, and the number of attendees.
- **Cancel a Booking**: Users can cancel an existing reservation using a unique booking identifier.
- **View Reservations**: Users can retrieve a list of all current bookings for the conference room.

## Domain Model
The application revolves around a clear and focused domain model:

### Meeting Room
- Represents the conference room, which is the central entity managing all reservations.
- Has a maximum capacity of 20 people.
- Ensures that:
  - No two bookings overlap in time.
  - No booking exceeds the room's maximum capacity of 20 people.
- Provides operations:
  - **Book**: Creates a new reservation if the time slot is available and the number of attendees is valid (between 4 and 20, inclusive).
  - **Cancel**: Removes a specific reservation.
  - **List Bookings**: Returns all existing reservations.

### Booking
- Represents an individual reservation.
- Contains:
  - A unique identifier for the booking.
  - Start time and end time of the reservation.
  - Details of the person making the booking (e.g., name or ID).
  - Number of attendees for the reservation (must be at least 4).
- Ensures that the number of attendees is at least 4.

### Time Slot
- Defines a specific time period for a reservation, consisting of a start time and end time.
- Used to check for conflicts between bookings.

## Key Business Rules
- **No Overlapping Bookings**: The system prevents reserving the conference room for time slots that conflict with existing bookings.
- **Capacity Constraints**: Each booking must have between 4 and 20 attendees (inclusive).
- **Booking Integrity**: All operations on bookings (creation, cancellation) are managed through the conference room to ensure consistency.

## Example Operations
1. **Booking a Room**:
   - Input: Start time, end time, booker details, and number of attendees.
   - Process: The system checks if the requested time slot is free and if the number of attendees is between 4 and 20. If both conditions are met, a new booking is created and added to the room's reservation list.
   - Output: Confirmation of the booking or an error if the slot is taken or the number of attendees is invalid.

2. **Canceling a Booking**:
   - Input: Unique booking identifier.
   - Process: The system removes the specified booking from the room's reservation list.
   - Output: Confirmation of cancellation.

3. **Viewing Reservations**:
   - Input: None.
   - Process: The system retrieves and returns a list of all bookings for the conference room.
   - Output: A list of bookings with their details (start time, end time, booker, number of attendees).

## Extensibility
The system is designed to be simple but can be extended to include features such as:
- User authentication and authorization.
- Integration with external calendar systems.
- Management of additional resources (e.g., projectors or other equipment).