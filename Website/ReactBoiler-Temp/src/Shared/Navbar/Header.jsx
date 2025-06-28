"use client"

import { useContext } from "react"
import { Link, useLocation } from "react-router-dom"
import { AuthContext } from "../../Providers/AuthProvider"
import {
  Navbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  Button,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  Link as NextUILink,
  Avatar,
} from "@nextui-org/react"

const SRELogo = () => {
  return (
    <svg fill="none" height="36" viewBox="0 0 32 32" width="36">
      <path
        clipRule="evenodd"
        d="M16 2L4 8v8c0 7.3 5.1 14.1 12 16 6.9-1.9 12-8.7 12-16V8L16 2z"
        fill="black"
        fillRule="evenodd"
      />
      <path
        d="M11 16l2 2 8-8"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export default function Header() {
  const { user, signOutUser } = useContext(AuthContext)
  const location = useLocation()

  const handleLogOut = () => {
    signOutUser().then().catch()
  }

  return (
    <Navbar className="bg-white border-b border-gray-200">
      <NavbarBrand>
        <Link to="/" className="flex items-center gap-3">
          <SRELogo />
          <p className="font-bold text-inherit text-2xl text-black">DeployRight</p>
        </Link>
      </NavbarBrand>

      <NavbarContent className="hidden sm:flex gap-4" justify="center">
        <NavbarItem isActive={location.pathname === "/features"}>
          <NextUILink
            as={Link}
            color={location.pathname === "/features" ? "primary" : "foreground"}
            to="/features"
            className="text-black text-lg font-medium hover:text-gray-600 transition-colors duration-300 ease-in-out"
          >
            Features
          </NextUILink>
        </NavbarItem>
        <NavbarItem isActive={location.pathname === "/pricing"}>
          <NextUILink
            as={Link}
            color={location.pathname === "/pricing" ? "primary" : "foreground"}
            to="/pricing"
            className="text-black text-lg font-medium hover:text-gray-600 transition-colors duration-300 ease-in-out"
          >
            Pricing
          </NextUILink>
        </NavbarItem>
        <NavbarItem isActive={location.pathname === "/docs"}>
          <NextUILink
            as={Link}
            color={location.pathname === "/docs" ? "primary" : "foreground"}
            to="/docs"
            className="text-black text-lg font-medium hover:text-gray-600 transition-colors duration-300 ease-in-out"
          >
            Docs
          </NextUILink>
        </NavbarItem>
        {user && (
          <NavbarItem isActive={location.pathname === "/agent"}>
            <NextUILink
              as={Link}
              color={location.pathname === "/agent" ? "primary" : "foreground"}
              to="/agent"
              className="text-black text-lg font-medium hover:text-gray-600 transition-colors duration-300 ease-in-out"
            >
              Dashboard
            </NextUILink>
          </NavbarItem>
        )}
      </NavbarContent>

      <NavbarContent justify="end">
        {user ? (
          <Dropdown placement="bottom-end">
            <DropdownTrigger>
              <button className="flex items-center gap-2 rounded-full transition-colors hover:bg-gray-100 px-3 py-2">
                <span className="hidden text-sm font-medium md:block text-black">
                  {user.displayName?.split(" ")[0] || "User"}
                </span>
                <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center text-white text-sm font-bold">
                  {(user.displayName?.charAt(0) || "U").toUpperCase()}
                </div>
              </button>
            </DropdownTrigger>
            <DropdownMenu aria-label="User menu" variant="flat" className="mt-3 ml-14 bg-white border border-gray-200 shadow-lg">
              <DropdownItem key="profile" textValue="Profile" className="text-black hover:bg-gray-100">
                <Link to="/profile" className="w-full">
                  Profile
                </Link>
              </DropdownItem>
              <DropdownItem key="dashboard" textValue="Dashboard" className="text-black hover:bg-gray-100">
                <Link to="/agent" className="w-full">
                  Dashboard
                </Link>
              </DropdownItem>
              <DropdownItem key="settings" textValue="Settings" className="text-black hover:bg-gray-100">
                <Link to="/settings" className="w-full">
                  Settings
                </Link>
              </DropdownItem>
              <DropdownItem
                key="logout"
                className="text-red-600 hover:bg-red-50"
                color="danger"
                onPress={handleLogOut}
              >
                Log Out
              </DropdownItem>
            </DropdownMenu>
          </Dropdown>
        ) : (
          <>
            <NavbarItem className="hidden lg:flex">
              <NextUILink
                as={Link}
                to="/login"
                className="text-black text-lg font-medium hover:text-gray-600 transition-colors duration-300 ease-in-out"
              >
                Login
              </NextUILink>
            </NavbarItem>
            <NavbarItem>
              <Button
                as={Link}
                to="/register"
                className="bg-black text-white font-medium hover:bg-gray-800 transition-all"
                size="sm"
              >
                Get Started
              </Button>
            </NavbarItem>
          </>
        )}
      </NavbarContent>
    </Navbar>
  )
}
