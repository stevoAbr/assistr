import React from "react"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import { 
  OpportunityPage,
  LandingPage, 
  Layout, 
  LoginPage, 
  NotFoundPage, 
  ProfilePage, 
  ProtectedRoute,
  OrgRoute,
  RegistrationPage,
  OrgRegistrationPage,
  OrgProfileEdit,
  ProfileRoute,
  OrgProfilePage,
  OrgOpportunities,
  Org0pportunities,
  Org0pportunitiesStatic,
  Chat,
  ChatOrg
} from "../../components"

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/org/chat" element={<ChatOrg />} />
          <Route
              path="/opportunities/*"
              element={<OpportunityPage/>}
            />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/profile" element={<ProtectedRoute component={ProfilePage} />} />  
          <Route path="/registration" element={<RegistrationPage />} />
          <Route path="/registration/org" element={<OrgRegistrationPage />} />
          <Route
              path="/edit-profile/*"
              element={<ProfileRoute component={OrgProfileEdit} />}
            />
          <Route path="/org-profile" element={<OrgProfilePage />} />
          <Route path="/org-profile/CreatedOpportunities/num=1" element={<Org0pportunitiesStatic />} />
          <Route path="/org-profile/createdOpportunities" element={<OrgOpportunities />} />
          <Route path="/org-profile/created0pportunities" element={<Org0pportunities />} />

          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}