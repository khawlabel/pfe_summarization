export const getAuthConfig = () => {
  const user = localStorage.getItem("user")
    ? JSON.parse(localStorage.getItem("user"))
    : null;

  return {
    headers: {
      Authorization: `Bearer ${user?.access_token || ""}`,
      Accept: "application/json",
    },
  };
};
