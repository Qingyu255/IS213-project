export type User = {
  isLoggedIn: boolean;
  username?: string;
  id?: string; // Don't mistake this for sub; this id is generated bu userManagementService
// eslint-disable-next-line @typescript-eslint/no-explicit-any
} & Record<string, any>;
