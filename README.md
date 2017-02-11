# email-scheduler-server
Server app to schedule emails

#Endpoints

[GET /emails](https://email-scheduler-api.herokuapp.com/emails)

[POST /save_emails](https://email-scheduler-api.herokuapp.com/save_emails)
Params:
- event_id: integer
- email_subject: string
- email_content: string
- timestamp ISO8601: string
