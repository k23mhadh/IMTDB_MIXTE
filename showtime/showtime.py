import grpc
from concurrent import futures
import json
import showtime_pb2
import showtime_pb2_grpc


class ShowtimeServicer(showtime_pb2_grpc.ShowtimeServicer):

    def __init__(self):
        with open('{}/data/times.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["schedule"]

    # Implement the GetSchedule RPC method
    def GetSchedule(self, request, context):
        schedule_response = showtime_pb2.ScheduleResponse()
        
        for day in self.db:
            schedule_day = showtime_pb2.ScheduleDay(date=day["date"])
            schedule_day.movies.extend(day["movies"])  # Add movies to the schedule_day
            schedule_response.schedule.append(schedule_day)
        
        return schedule_response

    # Implement the GetMoviesByDate RPC method
    def GetMoviesByDate(self, request, context):
        for day in self.db:
            if str(day["date"]) == request.date:  # Match the date from the request
                schedule_day = showtime_pb2.ScheduleDay(date=day["date"])
                schedule_day.movies.extend(day["movies"])  # Add movies to the schedule_day
                return showtime_pb2.MoviesByDateResponse(schedule_day=schedule_day)

        # If no movies are found for the specified date, return an empty response
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('No movies found for the specified date')
        return showtime_pb2.MoviesByDateResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    showtime_pb2_grpc.add_ShowtimeServicer_to_server(ShowtimeServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
