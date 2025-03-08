"use client";

import type React from "react";
import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import type { User } from "@/types/user";
import { getBearerToken } from "@/utils/auth";
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { UserDetailsSkeleton } from "../components/user-details-skeleton";
import { Edit, Save, Trash } from "lucide-react";
import { ErrorMessageCallout } from "@/components/error-message-callout";
import { getErrorStringFromResponse } from "@/utils/common";
import { toast } from "sonner";
import { UpdateUserDto } from "@/types/UpdateUserDto";
import { Route } from "@/enums/Route";
import { Spinner } from "@/components/ui/spinner";
import { ConfirmationPopover } from "@/components/confirmation-popover";
import Link from "next/link";
import { Separator } from "@/components/ui/separator";

export default function ViewEditUserPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [editableFields, setEditableFields] = useState<UpdateUserDto>({
    email: "",
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  const params = useParams();
  const userId = params.id as string;

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch(
          `${BACKEND_ROUTES.userManagementServiceUrl}/api/users/${userId}`,
          {
            method: "GET",
            headers: {
              Authorization: await getBearerToken(),
            },
          }
        );

        if (!res.ok) {
          const errorString = await getErrorStringFromResponse(res);
          console.error("An error occurred while fetching user details:", errorString);
          setError(errorString);
          toast.error("Error", {
            description: "Failed to fetch user details: " + errorString,
          });
          return;
        }

        const data: User = await res.json();
        setUser(data);
        setEditableFields({
          email: data.email,
        });
      } catch (err) {
        setError("Failed to load user data: " + err);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [userId]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setEditableFields((prev) => ({ ...prev, [name]: value }));
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    try {
      const res = await fetch(
        `${BACKEND_ROUTES.userManagementServiceUrl}/api/users/update/${userId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: await getBearerToken(),
          },
          body: JSON.stringify(editableFields),
        }
      );

      if (!res.ok) {
        const errorString = await getErrorStringFromResponse(res);
        console.error("An error occurred while updating user:", errorString);
        setError(errorString);
        toast("Error", {
          description: "Failed to update user: " + errorString,
        });
        return;
      }

      const updatedUser = await res.json();
      setUser(updatedUser);
      toast("Success", {
        description: "User updated successfully",
      });
      setIsEditing(false);
    } catch (err) {
      setError("Error updating user: " + err);
      toast("Error", {
        description: "Failed to update user"
      });
    }
  };

  const handleDeleteUser = async ( userId: string ) => {
    try {
      setLoading(true);
      const res = await fetch(
        `${BACKEND_ROUTES.userManagementServiceUrl}/api/users/delete/${userId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: await getBearerToken(),
          },
        }
      );

      if (!res.ok) {
        const errorString = await getErrorStringFromResponse(res);
        console.error("An error occurred while deleting user:", errorString);
        setError(errorString);
        toast.error("Error", {
          description: "Failed to delete user: " + errorString,
        });
        return;
      }
      toast("Success", {
        description: "User deleted successfully",
      });
      router.push(Route.BrowseEvents);
    } catch (err) {
      setError("Error: " + err);
      toast.error("error", {
        description: "Failed to delete user: " + err,
      });
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <UserDetailsSkeleton />
  };

  if (error) {
    return (
      <div className="p-4">
        <ErrorMessageCallout errorMessage={error} />
      </div>
    )
  };

  if (!user) {
    return <div>User not found</div>
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">User Details</h1>
      <form onSubmit={handleUpdate} className="space-y-4">
        <div>
          <Label htmlFor="id">ID</Label>
          <Input id="id" name="id" value={user.id} disabled />
        </div>
        <div>
          <Label htmlFor="username">Username</Label>
          <Input id="username" name="username" value={user.username} disabled />
        </div>
        <div>
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            value={isEditing ? editableFields.email : user.email}
            onChange={handleInputChange}
            disabled={!isEditing}
          />
          {isEditing && (
            <p className="text-red-600 my-1">Note that you will need to confirm your email again once updated.</p>
          )}
        </div>
        <div className="flex justify-end space-x-2">
          {isEditing ? (
            <>
              <Button type="submit">
                <Save/>
                Save Changes
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setIsEditing(false);
                  setEditableFields({
                    email: user.email,
                  });
                }}
              >
                Cancel
              </Button>
            </>
          ) : (
            <Button type="button" onClick={() => setIsEditing(true)}>
              <Edit/>
              Edit
            </Button>
          )}
          <ConfirmationPopover
            message={`Are you sure you want to delete user: ${user.username}?`}
            onConfirm={() => handleDeleteUser(user.id ?? "")}
          >
            <Button
              variant={"outline"}
              className="flex flex-row gap-x-2"
            >
              <Trash size={15} color="red" />
              Delete User
              {loading && (
                <Spinner className="bg-black dark:bg-white"/>
              )}
            </Button>
          </ConfirmationPopover>
        </div>
      </form>
      {error && (
        <div className="pt-3">
          <ErrorMessageCallout errorHeader="Error" errorMessage={error} />
        </div>
      )}
      <Separator className="my-3"/>
      <div className="flex space-y-2 justify-end">
        <Link href={`${Route.IndicateInterestCategories}/${userId}`}>
          <Button>
            Manage My Interests
          </Button>
        </Link>
      </div>
    </div>
  );
}
