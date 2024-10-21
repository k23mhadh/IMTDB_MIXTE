import grpc
from concurrent import futures
import json
import booking_pb2
import booking_pb2_grpc
import showtime_pb2
import showtime_pb2_grpc

class BookingService(booking_pb2_grpc.BookingServiceServicer):

    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

        # Create a gRPC channel to the Showtime service
        self.showtime_channel = grpc.insecure_channel('localhost:3002')
        self.showtime_stub = showtime_pb2_grpc.ShowtimeStub(self.showtime_channel)

    # Implement the GetAllBookings RPC method
    def GetAllBookings(self, request, context):
        response = booking_pb2.BookingList()
        for b in self.db:
            booking_obj = booking_pb2.Booking(userid=b["userid"])
            for d in b["dates"]:
                date_obj = booking_pb2.BookingDate(date=d["date"])
                date_obj.movies.extend(d["movies"])
                booking_obj.dates.append(date_obj)
            response.bookings.append(booking_obj)
        return response

    # Implement the GetUserBookings RPC method
    def GetUserBookings(self, request, context):
        for booking in self.db:
            if str(booking["userid"]) == request.userid:
                booking_obj = booking_pb2.Booking(userid=booking["userid"])
                for date in booking["dates"]:
                    date_obj = booking_pb2.BookingDate(date=date["date"])
                    date_obj.movies.extend(date["movies"])
                    booking_obj.dates.append(date_obj)
                return booking_obj

        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('No bookings found for the specified user')
        return booking_pb2.Booking()

    # Implement the CreateBooking RPC method
    def CreateBooking(self, request, context):
        userid = request.userid
        movieid = request.movieid
        date = request.date

        # Call Showtime service to check if the movie is available on the given date
        movies_request = showtime_pb2.MoviesByDateRequest(date=date)
        try:
            showtimes_response = self.showtime_stub.GetMoviesByDate(movies_request)
            if movieid not in showtimes_response.schedule_day.movies:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details('Movie not found for the given date')
                return booking_pb2.BookingResponse(message="Movie not found for the given date")
        except grpc.RpcError as e:
            context.set_code(e.code())
            context.set_details(e.details())
            return booking_pb2.BookingResponse(message="Failed to retrieve showtimes")

        # Proceed with booking logic
        existing_booking = next((b for b in self.db if b["userid"] == userid), None)

        if existing_booking:
            existing_date_obj = next((d for d in existing_booking["dates"] if d["date"] == date), None)
            if existing_date_obj:
                if movieid in existing_date_obj["movies"]:
                    context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                    context.set_details('Booking already exists')
                    return booking_pb2.BookingResponse(message="Booking already exists")
                else:
                    existing_date_obj["movies"].append(movieid)
            else:
                existing_booking["dates"].append({
                    "date": date,
                    "movies": [movieid]
                })
        else:
            self.db.append({
                "userid": userid,
                "dates": [
                    {
                        "date": date,
                        "movies": [movieid]
                    }
                ]
            })

        # Write updated bookings to the file
        with open('./data/bookings.json', 'w') as f:
            json.dump({"bookings": self.db}, f)

        return booking_pb2.BookingResponse(message="Booking created")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServiceServicer_to_server(BookingService(), server)
    server.add_insecure_port('[::]:3003')
    server.start()
    print("Booking gRPC server running on port 3003")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
