GitHub repository for Knit

The Weavers (Team 8) will be creating an app called
“Knit” in response to the changing dynamics observed in this
college town. People come and go, and individuals with whom one
once shared hobbies may no longer be in the same town after
graduating. There are times when an individual would like to find
someone to join them in an activity, such as running, playing board
games, or practicing a dance, but they may not know where to find
people who are also interested in participating. Currently,
invitations to participate in group activities are often scattered
across different platforms, such as Facebook, Reddit, and group
chats. Therefore, the Weavers would like to create an app that
brings people with similar interests together, allows them to
participate in activities, and helps them build new friendships.

## API

The project includes an Activities API endpoint that returns activity data in JSON format.

- `/api/activities/` returns all activities using `JsonResponse`.
- `/api/activities/?q=run` filters activities using the `q` query parameter.
- `/api/activities-http/` returns the same activity data using a standard `HttpResponse` for comparison.

The JSON API returns activity IDs and activity names from the Activities model.