import { useState, type FormEvent } from "react";
import { useAddMember, useMembers, useRemoveMember } from "@/api/hooks";
import type { Member, ResearchGroupRole } from "@/api/types";
import { asCurie, bareOrcid, signedInUser } from "@/identity";
import Modal from "@/components/Modal";
import ConfirmDialog from "@/components/ConfirmDialog";
import RowMenu, { RowMenuItem } from "@/components/RowMenu";
import { TrashIcon, UserIcon } from "@/components/icons";
import {
  MemberAvatar,
  MemberName,
  MemberOrcid,
  MemberRole,
  MemberRow,
  MemberWho,
  MembersAdd,
  MembersDivider,
  MembersList,
  MembersSubhead,
  ModalActions,
  ModalBanded,
  ModalBody,
  ModalFoot,
  ModalHead,
  ModalInput,
  ModalSelect,
  ModalText,
  ModalTitle,
} from "@/styles/elements";

const ROLES: ResearchGroupRole[] = ["member", "admin"];

const roleLabel = (role: ResearchGroupRole) =>
  role === "admin" ? "Admin" : "Member";

/**
 * Initials from a name. Every ORCID opens with the same digits, so without a
 * name the avatar says nothing and is left blank.
 */
const initials = (member: Member) =>
  member.name
    ?.split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase() ?? "";

/**
 * A group's members, and for an admin the controls to change them.
 *
 * The response carries each membership's ORCID but not the person's name, so
 * rows fall back to the identifier. `name` is read as optional, and names
 * appear on their own once the field is served.
 */
const MembersForm = ({
  groupId,
  open,
  onClose,
}: {
  groupId: number;
  open: boolean;
  onClose: () => void;
}) => {
  const [orcid, setOrcid] = useState("");
  const [role, setRole] = useState<ResearchGroupRole>("member");
  const [removing, setRemoving] = useState<Member | null>(null);

  const { data: members = [] } = useMembers(groupId);
  const addMember = useAddMember(groupId);
  const removeMember = useRemoveMember(groupId);

  const me = signedInUser();
  const myCurie = me ? asCurie(me.orcid_id) : null;
  // Whoever is signed in reads their own role off the list.
  const isAdmin = members.some(
    (each) => each.member === myCurie && each.role === "admin",
  );

  const close = () => {
    addMember.reset();
    setOrcid("");
    setRole("member");
    onClose();
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    addMember.mutate(
      { member: asCurie(bareOrcid(orcid.trim())), role },
      { onSuccess: () => setOrcid("") },
    );
  };

  const confirmRemove = () => {
    if (!removing) return;
    removeMember.mutate(removing.id, { onSuccess: () => setRemoving(null) });
  };

  return (
    <>
      <Modal open={open} title="Members" onClose={close} isWide>
        <ModalBanded>
          <ModalHead>
            <ModalTitle>Members</ModalTitle>
            <ModalText>
              Who can see and curate this group&rsquo;s submissions.
            </ModalText>
          </ModalHead>

          <ModalBody>
            <MembersSubhead>Current members ({members.length})</MembersSubhead>
            <MembersList>
              {members.map((member) => (
                <MemberRow key={member.id}>
                  <MemberAvatar aria-hidden="true">
                    {initials(member) || <UserIcon />}
                  </MemberAvatar>
                  <MemberWho>
                    <MemberName>{member.name ?? bareOrcid(member.member)}</MemberName>
                    {member.name && (
                      <MemberOrcid>ORCID: {bareOrcid(member.member)}</MemberOrcid>
                    )}
                  </MemberWho>
                  <MemberRole isAdmin={member.role === "admin"}>
                    {roleLabel(member.role)}
                  </MemberRole>
                  {/* No self-removal: an admin can drop others, not their own
                      seat, which would leave the group without one. */}
                  {isAdmin && member.member !== myCurie && (
                    <RowMenu label={`Actions for ${bareOrcid(member.member)}`}>
                      <RowMenuItem
                        icon={<TrashIcon />}
                        label="Remove"
                        danger
                        onClick={() => setRemoving(member)}
                      />
                    </RowMenu>
                  )}
                </MemberRow>
              ))}
            </MembersList>

            {isAdmin && (
              <>
                <MembersDivider />
                <MembersSubhead>Add member</MembersSubhead>
                <ModalText>
                  Enter an ORCID and choose a role. Their name appears once they
                  have signed in.
                </ModalText>
                <MembersAdd onSubmit={submit}>
                  <ModalInput
                    value={orcid}
                    onChange={(e) => setOrcid(e.target.value)}
                    required
                    placeholder="e.g. 0000-0002-1825-0097"
                    aria-label="ORCID"
                  />
                  <ModalSelect
                    value={role}
                    onChange={(e) => setRole(e.target.value as ResearchGroupRole)}
                    aria-label="Role"
                  >
                    {ROLES.map((each) => (
                      <option key={each} value={each}>
                        {roleLabel(each)}
                      </option>
                    ))}
                  </ModalSelect>
                  <button
                    className="btn btn--primary"
                    type="submit"
                    disabled={addMember.isPending}
                  >
                    {addMember.isPending ? "Adding…" : "Add member"}
                  </button>
                </MembersAdd>
                {addMember.error && (
                  <ModalText role="alert">{addMember.error.message}</ModalText>
                )}
              </>
            )}
          </ModalBody>

          <ModalFoot>
            <ModalActions>
              <button className="btn btn--secondary" type="button" onClick={close}>
                Done
              </button>
            </ModalActions>
          </ModalFoot>
        </ModalBanded>
      </Modal>

      <ConfirmDialog
        open={removing !== null}
        title="Remove member"
        message={`Remove ${removing ? bareOrcid(removing.member) : ""} from this group?`}
        isPending={removeMember.isPending}
        error={removeMember.error?.message}
        onConfirm={confirmRemove}
        onClose={() => setRemoving(null)}
      />
    </>
  );
};

export default MembersForm;
