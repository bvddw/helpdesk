# Helpdesk Project Documentation
## Application Description

Helpdesk is a web application designed for managing service requests and assistance inquiries. Users can create requests with topics, descriptions, and priority levels. Requests go through various statuses, and administrators have the capability to manage these statuses. 

## Roles and Capabilities
### Administrator (Admin)

Administrators have full control over request management and comments. Their capabilities include:

* Viewing all requests, including requests from all users.
* Changing request statuses:
     *    Changing `Active` status to `Approved` or `Declined` with a specified reason.
     *    Changing `Approved` status to `In Process`.
     *    Changing `In Process` status to `Completed`.
     *    Changing `Declined` status to `For Restoration` with a specified reason.
* Leaving comments on any requests in the `In Process` status.
* Viewing all comments on requests.
* Creating new requests with a subject, description, and priority. But they cannot change the status of their requests.

### Regular User (Regular)

Regular users can create and manage their own requests. Their capabilities include:

* Creating new requests with a subject, description, and priority.
* Viewing a list of their own requests in all statuses except `Active` and `For Restoration`.
* Editing their own requests.
* Deleting their own requests.
* Leaving comments on their own requests but only if the request is in the `In Process` status.

### Anonymous User (Anonymous)

Anonymous users have limited capabilities:

* Logging into the system with existing credentials.
* Registering new user accounts.

## Models
### HelpRequest

The HelpRequest model represents a request for assistance. It includes the following fields:

* `subject` - The subject of the request.
* `text` - The description of the request.
* `requester` - A link to the user who created the request.
* `priority` - The priority of the request (chosen from PriorityChoices).
* `status` - The current status of the request (chosen from StatusChoices).
* `created_at` - The date and time when the request was created.
* `updated_at` - The date and time of the last request update.

Possible requests priority:

- `Low` - Low priority.
- `Medium` - Medium priority.
- `High` - High priority.

Possible requests statuses:
- `Active` - An active request.
- `Declined` - A declined request, with a reason of declining.
- `For Restoration` - A request for restoration (equivalent to "Active", but after being declined).
- `Approved` - An approved request.
- `In Process` - A request in the process of being completed.
- `Completed` - A completed request.

**Note:** Request always creating with `Active` status, creator cannot pick status.

### Comment

The Comment model represents a comment on a request. It includes the following fields:

* `message` - The text of the comment.
* `author` - A link to the user who created the comment.
* `help_request` - A link to the request to which the comment belongs.
* `created_at` - The date and time when the comment was created.

### DeclinedRequest

The DeclinedRequest model represents a declined request and includes a reason for the decline. It includes the following fields:

* declined_request - A link to the request that was declined.
* comment - The reason for the request's decline.

This documentation provides a general overview of the application's functionality and models. Detailed implementation and usage of the application require appropriate programming and deployment.

## Relationships

#### User to Request
Each `User` can make multiple `HelpRequests`, but each `HelpRequest` refers to only one `User` - requester, forming a **many-to-one** relationship.

#### User to Comment
Each `User` can make multiple `Comments`, but each `Comment` refers to only one `User` - requester, forming a **many-to-one** relationship.

#### Comment to HelpRequest
Each `HelpRequest` can be associated with multiple `Comments`, but each `Comment` can be written under **one and only one** HelpRequest, forming a **many-to-one** relationship.

#### HelpRequest to DeclinedRequest
A `HelpRequest` may be declined by a `reason`, and for each declined request its own `reason`, so this forms a **one-to-one** relation between HelpRequest and DeclinedRequest.

## Django View Logic
#### Main view
Contains a list af links:
* For Admin
  * Link to request creation page
  * Link to the list with all requests
  * Link to the list with requests with `Active` status
  * Link to the list with requests with `For Restoration` status
* For Regular User
  * Link to request creation page
  * Link to the list with all requests, created by this user, without requests with status `Active` or `For Restoration`

Each authenticated user can check their requests, and only their. 
User could check requests in view with a list of them. Also, user could check each request in details.

#### List view
Contains a list of requests, separated in three columns:

`Low priority | Medium priority | High priority`

Each request in the list contains the subject, a part of text, created date and status.

Each subject is clickable, and redirect user on detail view.

#### Detail view

Contains whole information about request:
* Subject
* created at
* last update
* requester username
* status
* priority
* text
* buttons for updating and deleting
* * `admin`: button for changing status, dependency on current status 
  * `user`: only button `Resend Review`, if request was declined
* form for comments, if current status is `In process`
* comments, if they exist

#### Create view
Contains a creation form. Fields:
* `Subject`
* `Text` (description)
* `Priority`
* Button for a submitting form and create request
* Button for returning on the main view

#### Update view
Contains an update form. Fields:
* `Subject` (without possibility of updating)
* `Text` (description)
* `Priority`
* Button for a submitting form and update request
* Button for returning on the main view

#### Delete view
Contains an delete confirmation. Buttons:
* `Delete` - redirect on the main view
* `Cancel` - back to the detail vew

#### About us view
Contains information about a Helpdesk company.

#### Login View
Contains a form for login. Fields:
* Username
* Password

#### Registration view
Contains a form for register. Fields:
* Username
* Password
* Confirm password

#### Views for changing status
without templates

## Django-Rest View Logic
### Token Retrieval View

The token retrieval view allows users to obtain authentication tokens to access the system. This is typically part of user authentication and login processes. Users can request and receive tokens to authenticate themselves in subsequent requests.

In this section, we'll describe the view logic for managing requests in the Django-Rest framework. The logic covers how requests are viewed and manipulated by users with different roles, such as administrators and regular users. Additionally, we'll touch on views related to token retrieval, restoration requests (accessible only to administrators), and status changes as previously explained.
### Request Model Viewset

The Request model viewset is responsible for managing service requests. It defines how requests are viewed and modified based on the user's role.
#### Administrator View
* View All Requests: Administrators have the privilege to view all requests. They can access a list of all service requests regardless of the user who created them. This view displays all the requests in the system. Allow methods for admin - `retrieve` and `post`. About `update`, `partial update`, `delete` - only for requests, in which they are requesters.

#### Regular User View

* View Own Requests: Regular users can only view their own requests. This view displays a list of the user's service requests, excluding requests in the "Active" and "For Restoration" statuses.

* Modify and Delete: Regular users can modify and delete their own requests. This allows them to edit the content and, if needed, remove their requests from the system.

### Restoration Requests View

This view is exclusively available to administrators. It allows administrators to access and review service requests in the "For Restoration" status. These requests are those that were initially declined but can be resubmitted for approval. Administrators can evaluate these requests and decide whether to approve or decline them again.
### Status Change Views

Status change views enable users to modify the status of service requests. The available status transitions are as follows:

* `Active` to `Approved`/`Declined`: Administrators can change the status of `Active` requests to `Approved` or `Declined` and provide a reason for the declining.

* `Approved` to `In Process`: Administrators can transition requests in the `Approved` status to `In Process`. This signifies that the request is currently being addressed.

* `In Process` to `Completed`: Administrators can change the status of requests in the `In Process` stage to `Completed` once the request is successfully resolved.

* `Declined` to `For Restoration`: Administrators can move requests in the `Declined` status to `For Restoration` if they believe the request should be reevaluated. A reason should be provided for this transition.

These views are responsible for handling status changes, allowing administrators to manage service requests efficiently.

### Comments Views
The Comments view is responsible for `get` the list of comments related to specific requests and `post` comments, following rules (can post only to request with `In Process` status). It allows users, including administrators and request creators, to retrieve and create comments for a chosen request.

This logic and viewset structure allow for effective management of service requests and user roles within the Django-Rest framework.
