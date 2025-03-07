export type User = {
    isLoggedIn: boolean;
    username?: string;
  } & Record<string, unknown>;
  