# Github workflows

This application uses [Github Actions](https://github.com/features/actions) to run CI/CD and other workflows.
ITS CURRENTLY A WIP.

## Workflows

The workflows have been divided per service on for two events (Push, Pull Request).

-   When a pull request is made, the CI part of the application kicks off. The definition can be found in the file `pull-request-xxx.yml` where xxx is the client/server.
