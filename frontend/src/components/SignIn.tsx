import { useState } from "react";

import { useSignIn } from "../api/queries";

export function SignIn() {
  const [username, setUsername] = useState("");
  const signIn = useSignIn();

  return (
    <div className="flex min-h-dvh items-center justify-center bg-slate-100 p-4">
      <form
        className="w-full max-w-sm space-y-4 rounded-xl bg-white p-8 shadow-sm"
        onSubmit={(event) => {
          event.preventDefault();
          signIn.mutate(username.trim());
        }}
      >
        <h1 className="text-2xl font-bold text-slate-900">
          Pokémon Team Builder
        </h1>
        <div className="space-y-1">
          <label
            className="block text-sm font-medium text-slate-700"
            htmlFor="username"
          >
            Username
          </label>
          <input
            id="username"
            className="field w-full px-3 py-2"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoFocus
          />
        </div>
        <button
          type="submit"
          disabled={!username.trim() || signIn.isPending}
          className="primary-button w-full py-2 font-medium"
        >
          {signIn.isPending ? "Signing in…" : "Sign in"}
        </button>
        {signIn.isError && (
          <p className="text-sm text-red-600">
            Could not sign in. Is the API running?
          </p>
        )}
      </form>
    </div>
  );
}
